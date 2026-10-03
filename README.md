# TSIS

University coursework in Python: three Pygame games and a console phonebook with PostgreSQL. These are extended versions of the games from [Practice-10](https://github.com/kashanqq/Practice-10).

## Projects

### `snake/`

Snake with levels and a database.

- Levels with obstacles that grow in number
- Several food types: normal, weighted, disappearing and poison
- Timed power-ups
- Player names and personal best scores stored in PostgreSQL

```bash
cd snake
docker compose up -d
python main.py
```

### `racer/`

A lane racer with a menu, settings and a leaderboard.

- Sound, car color and difficulty settings
- Settings and leaderboard saved to JSON files

```bash
cd racer
python main.py
```

### `paint/`

A drawing app with a toolbar.

- Shape tools, color and brush width selection
- Flood fill

```bash
cd paint
python main.py
```

### `phonebook/`

A console phonebook on PostgreSQL.

- Contacts with groups and several phone numbers each
- Search, filter by group and paginated view
- Import from CSV and JSON, export to JSON
- Stored procedures for upserts (`init.sql`)

```bash
cd phonebook
docker compose up -d
python main.py
```

Database settings are read from a `.env` file: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASS`, `DB_NAME`.

## Requirements

Python 3, `pygame`, `psycopg2`, `python-dotenv`, Docker for the databases

```bash
pip install pygame psycopg2-binary python-dotenv
```
