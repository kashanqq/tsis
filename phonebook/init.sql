-- Schema creation
CREATE TABLE groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE contacts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(100),
    birthday DATE,
    group_id INTEGER REFERENCES groups(id) ON DELETE SET NULL,
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE phones (
    id SERIAL PRIMARY KEY,
    contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE,
    phone VARCHAR(20) NOT NULL,
    type VARCHAR(10) CHECK (type IN ('home', 'work', 'mobile'))
);

-- Practice 8 Procedures

-- Upsert Procedure
CREATE OR REPLACE PROCEDURE upsert_contact(
    p_name VARCHAR,
    p_email VARCHAR,
    p_birthday DATE,
    p_group_name VARCHAR,
    p_phone VARCHAR,
    p_phone_type VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_group_id INTEGER;
    v_contact_id INTEGER;
BEGIN
    -- Handle group
    IF p_group_name IS NOT NULL THEN
        SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;
        IF NOT FOUND THEN
            INSERT INTO groups (name) VALUES (p_group_name) RETURNING id INTO v_group_id;
        END IF;
    END IF;

    -- Upsert contact
    INSERT INTO contacts (name, email, birthday, group_id)
    VALUES (p_name, p_email, p_birthday, v_group_id)
    ON CONFLICT (name) DO UPDATE 
    SET email = EXCLUDED.email, 
        birthday = EXCLUDED.birthday, 
        group_id = EXCLUDED.group_id
    RETURNING id INTO v_contact_id;
    
    -- Handle phone
    IF p_phone IS NOT NULL THEN
        IF NOT EXISTS (SELECT 1 FROM phones WHERE contact_id = v_contact_id AND phone = p_phone) THEN
            INSERT INTO phones (contact_id, phone, type)
            VALUES (v_contact_id, p_phone, p_phone_type);
        END IF;
    END IF;
END;
$$;

-- Delete by Name or Phone Procedure
CREATE OR REPLACE PROCEDURE delete_contact(p_identifier VARCHAR)
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM phones WHERE phone = p_identifier) THEN
        DELETE FROM contacts WHERE id IN (SELECT contact_id FROM phones WHERE phone = p_identifier);
    ELSE
        DELETE FROM contacts WHERE name = p_identifier;
    END IF;
END;
$$;

-- Paginated Query Function
CREATE OR REPLACE FUNCTION get_contacts_paginated(
    p_limit INTEGER,
    p_offset INTEGER,
    p_sort_col VARCHAR DEFAULT 'name'
)
RETURNS TABLE (
    contact_id INTEGER,
    name VARCHAR,
    email VARCHAR,
    birthday DATE,
    group_name VARCHAR,
    date_added TIMESTAMP
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- We use dynamic SQL to allow sorting by a specified column
    RETURN QUERY EXECUTE format('
        SELECT c.id, c.name, c.email, c.birthday, g.name, c.date_added
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        ORDER BY %I
        LIMIT $1 OFFSET $2', p_sort_col)
    USING p_limit, p_offset;
END;
$$;


-- Practice 9 Procedures

-- Add Phone Procedure
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone VARCHAR,
    p_type VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INTEGER;
BEGIN
    SELECT id INTO v_contact_id FROM contacts WHERE name = p_contact_name;
    
    IF FOUND THEN
        INSERT INTO phones (contact_id, phone, type) VALUES (v_contact_id, p_phone, p_type);
    ELSE
        RAISE EXCEPTION 'Contact % not found', p_contact_name;
    END IF;
END;
$$;

-- Move to Group Procedure
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_group_id INTEGER;
BEGIN
    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;
    IF NOT FOUND THEN
        INSERT INTO groups (name) VALUES (p_group_name) RETURNING id INTO v_group_id;
    END IF;
    
    UPDATE contacts SET group_id = v_group_id WHERE name = p_contact_name;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Contact % not found', p_contact_name;
    END IF;
END;
$$;

-- Pattern Search Function
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    contact_id INTEGER,
    name VARCHAR,
    email VARCHAR,
    birthday DATE,
    group_name VARCHAR,
    phone VARCHAR,
    phone_type VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
        SELECT c.id, c.name, c.email, c.birthday, g.name, p.phone, p.type
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        WHERE c.name ILIKE '%' || p_query || '%'
           OR c.email ILIKE '%' || p_query || '%'
           OR p.phone ILIKE '%' || p_query || '%';
END;
$$;
