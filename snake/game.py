import pygame
import random
from config import *

def generate_pos(snake_body, obstacles, other_items):
    while True:
        x = random.randrange(0, SCREEN_WIDTH, BLOCK_SIZE)
        y = random.randrange(0, SCREEN_HEIGHT, BLOCK_SIZE)
        pos = [x, y]
        if pos in snake_body:
            continue
        if obstacles and pos in obstacles:
            continue
        if other_items and pos in other_items:
            continue
        return pos

def generate_obstacles(snake_head, level):
    obstacles = []
    # Base number of obstacles increases with level starting from 3
    num_obstacles = (level - 2) * 5
    if num_obstacles <= 0:
        return obstacles
        
    for _ in range(num_obstacles):
        while True:
            x = random.randrange(0, SCREEN_WIDTH, BLOCK_SIZE)
            y = random.randrange(0, SCREEN_HEIGHT, BLOCK_SIZE)
            pos = [x, y]
            
            # Keep away from snake spawn point to avoid trapping
            dist_x = abs(x - snake_head[0])
            dist_y = abs(y - snake_head[1])
            if dist_x < BLOCK_SIZE * 5 and dist_y < BLOCK_SIZE * 5:
                continue
            
            if pos not in obstacles:
                obstacles.append(pos)
                break
    return obstacles

def get_food_color(ftype):
    if ftype == "normal": return FOOD_NORMAL_COLOR
    if ftype == "weighted": return FOOD_WEIGHTED_COLOR
    if ftype == "disappearing": return FOOD_DISAPPEARING_COLOR
    if ftype == "poison": return FOOD_POISON_COLOR
    return WHITE

def get_powerup_color(ptype):
    if ptype == "speed": return POWERUP_SPEED_COLOR
    if ptype == "slow": return POWERUP_SLOW_COLOR
    if ptype == "shield": return POWERUP_SHIELD_COLOR
    return WHITE

def run_game(screen, username, personal_best, clock):
    settings = load_settings()
    snake_color = tuple(settings.get("snake_color", GREEN))
    grid_overlay = settings.get("grid_overlay", True)
    
    snake_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
    # Ensure aligned to grid
    snake_pos[0] -= snake_pos[0] % BLOCK_SIZE
    snake_pos[1] -= snake_pos[1] % BLOCK_SIZE
    
    snake_body = [[snake_pos[0], snake_pos[1]], 
                  [snake_pos[0] - BLOCK_SIZE, snake_pos[1]], 
                  [snake_pos[0] - 2 * BLOCK_SIZE, snake_pos[1]]]
    
    change_to = "RIGHT"
    direction = "RIGHT"
    
    score = 0
    level = 1
    foods_eaten_in_level = 0
    base_fps = 10
    
    obstacles = generate_obstacles(snake_pos, level)
    
    # Food management
    # List of food dicts: {"pos": [x, y], "type": str, "spawn_time": int or None}
    foods = []
    
    def spawn_food():
        types = ["normal"] * 60 + ["weighted"] * 20 + ["disappearing"] * 10 + ["poison"] * 10
        ftype = random.choice(types)
        pos = generate_pos(snake_body, obstacles, [f["pos"] for f in foods])
        foods.append({"pos": pos, "type": ftype, "spawn_time": pygame.time.get_ticks()})

    spawn_food()

    # Power-up management
    powerup = None # {"pos": [x,y], "type": str, "spawn_time": int}
    active_powerup = None # {"type": str, "start_time": int}
    powerup_spawn_timer = pygame.time.get_ticks()
    
    shield_active = False

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return score, level, "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != "DOWN":
                    change_to = "UP"
                elif event.key == pygame.K_DOWN and direction != "UP":
                    change_to = "DOWN"
                elif event.key == pygame.K_LEFT and direction != "RIGHT":
                    change_to = "LEFT"
                elif event.key == pygame.K_RIGHT and direction != "LEFT":
                    change_to = "RIGHT"
        
        direction = change_to
        
        # Calculate new head
        new_head = list(snake_body[0])
        if direction == "UP": new_head[1] -= BLOCK_SIZE
        if direction == "DOWN": new_head[1] += BLOCK_SIZE
        if direction == "LEFT": new_head[0] -= BLOCK_SIZE
        if direction == "RIGHT": new_head[0] += BLOCK_SIZE
        
        # Border collision
        border_collided = False
        if new_head[0] < 0 or new_head[0] >= SCREEN_WIDTH or new_head[1] < 0 or new_head[1] >= SCREEN_HEIGHT:
            border_collided = True
            
        # Self collision
        self_collided = False
        if new_head in snake_body:
            self_collided = True
            
        # Obstacle collision
        obstacle_collided = False
        if new_head in obstacles:
            obstacle_collided = True
            
        if border_collided or self_collided or obstacle_collided:
            if shield_active:
                shield_active = False
                # Bounce back or ignore? The prompt says "Ignores the next wall or self-collision once".
                # To simply ignore, we can prevent the move and let player turn.
                # However, if moving into wall, best is to just not move head and let them turn.
                pass # Don't update head, snake pauses for a frame to let player turn
            else:
                return score, level, "game_over"
        else:
            snake_body.insert(0, new_head)
            
            # Check Food
            ate_food = False
            for f in foods[:]:
                if new_head == f["pos"]:
                    ate_food = True
                    foods.remove(f)
                    
                    if f["type"] == "normal":
                        score += 1
                        foods_eaten_in_level += 1
                    elif f["type"] == "weighted":
                        score += 3
                        foods_eaten_in_level += 1
                    elif f["type"] == "disappearing":
                        score += 2
                        foods_eaten_in_level += 1
                    elif f["type"] == "poison":
                        # Shorten by 2 segments
                        if len(snake_body) > 2:
                            snake_body.pop()
                            snake_body.pop()
                        else:
                            return score, level, "game_over"
                    break
            
            if not ate_food:
                snake_body.pop()
            
            # Check Power-up
            if powerup and new_head == powerup["pos"]:
                ptype = powerup["type"]
                if ptype == "shield":
                    shield_active = True
                else:
                    active_powerup = {"type": ptype, "start_time": current_time}
                powerup = None
                powerup_spawn_timer = current_time # Reset timer to delay next spawn

        # Level progression
        if foods_eaten_in_level >= 5:
            level += 1
            foods_eaten_in_level = 0
            obstacles = generate_obstacles(snake_body[0], level)
            
        # Food disappearing logic
        for f in foods[:]:
            if f["type"] == "disappearing":
                if current_time - f["spawn_time"] > 6000: # 6 seconds
                    foods.remove(f)
                    
        # Maintain at least one food
        if len(foods) == 0:
            spawn_food()
            
        # Powerup spawning/despawning
        if powerup:
            if current_time - powerup["spawn_time"] > 8000: # 8 seconds to collect
                powerup = None
                powerup_spawn_timer = current_time
        elif not active_powerup:
            if current_time - powerup_spawn_timer > 10000: # Spawn every 10 seconds of inactivity
                if random.random() < 0.5: # 50% chance to spawn
                    ptype = random.choice(["speed", "slow", "shield"])
                    pos = generate_pos(snake_body, obstacles, [f["pos"] for f in foods])
                    powerup = {"pos": pos, "type": ptype, "spawn_time": current_time}
                powerup_spawn_timer = current_time # Reset to try again later if it failed
                
        # Handle active powerups duration
        current_fps = base_fps + (level - 1) * 2
        if active_powerup:
            if current_time - active_powerup["start_time"] > 5000: # 5 seconds
                active_powerup = None
            else:
                if active_powerup["type"] == "speed":
                    current_fps += 10
                elif active_powerup["type"] == "slow":
                    current_fps = max(5, current_fps - 5)

        # Rendering
        screen.fill(BLACK)
        
        if grid_overlay:
            for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
                pygame.draw.line(screen, DARK_GRAY, (x, 0), (x, SCREEN_HEIGHT))
            for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
                pygame.draw.line(screen, DARK_GRAY, (0, y), (SCREEN_WIDTH, y))

        # Draw Obstacles
        for obs in obstacles:
            pygame.draw.rect(screen, OBSTACLE_COLOR, [obs[0], obs[1], BLOCK_SIZE, BLOCK_SIZE])
            
        # Draw Foods
        for f in foods:
            pygame.draw.rect(screen, get_food_color(f["type"]), [f["pos"][0], f["pos"][1], BLOCK_SIZE, BLOCK_SIZE])
            
        # Draw Powerup
        if powerup:
            # Draw as circle to distinguish from food
            center = (powerup["pos"][0] + BLOCK_SIZE//2, powerup["pos"][1] + BLOCK_SIZE//2)
            pygame.draw.circle(screen, get_powerup_color(powerup["type"]), center, BLOCK_SIZE//2)

        # Draw Snake
        for idx, block in enumerate(snake_body):
            color = snake_color
            if shield_active and idx == 0:
                color = POWERUP_SHIELD_COLOR # Head glows orange when shielded
            pygame.draw.rect(screen, color, [block[0], block[1], BLOCK_SIZE, BLOCK_SIZE])
            
        # UI overlays
        score_text = FONT_SMALL.render(f"Score: {score}", True, WHITE)
        level_text = FONT_SMALL.render(f"Level: {level}", True, WHITE)
        pb_text = FONT_SMALL.render(f"PB: {personal_best}", True, WHITE)
        
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 40))
        screen.blit(pb_text, (SCREEN_WIDTH - 150, 10))
        
        if active_powerup:
            rem_time = 5 - (current_time - active_powerup['start_time']) // 1000
            pw_text = FONT_SMALL.render(f"{active_powerup['type'].upper()} ({rem_time}s)", True, get_powerup_color(active_powerup["type"]))
            screen.blit(pw_text, (SCREEN_WIDTH // 2 - 50, 10))
        elif shield_active:
            pw_text = FONT_SMALL.render(f"SHIELD ACTIVE", True, POWERUP_SHIELD_COLOR)
            screen.blit(pw_text, (SCREEN_WIDTH // 2 - 50, 10))

        pygame.display.flip()
        clock.tick(current_fps)
