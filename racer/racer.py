import pygame
import random
import time
from pygame.locals import *
from ui import draw_hud
from persistence import load_settings

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 215, 0)
GRAY = (128, 128, 128)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

COLOR_MAP = {
    "red": RED,
    "green": GREEN,
    "blue": BLUE,
    "yellow": YELLOW
}

def create_surface(width, height, color, shape="rect"):
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    if shape == "rect":
        pygame.draw.rect(surf, color, surf.get_rect(), border_radius=5)
    elif shape == "circle":
        pygame.draw.circle(surf, color, (width//2, height//2), width//2)
    return surf

class Player(pygame.sprite.Sprite):
    def __init__(self, color_name):
        super().__init__()
        color = COLOR_MAP.get(color_name, BLUE)
        self.image = create_surface(40, 80, color)
        self.rect = self.image.get_rect()
        self.rect.center = (160, 520)
        self.active_powerup = None
        self.powerup_timer = 0
        self.has_shield = False

    def update_powerups(self, dt):
        if self.active_powerup:
            if self.active_powerup != "shield":
                self.powerup_timer -= dt
                if self.powerup_timer <= 0:
                    self.active_powerup = None
                    self.powerup_timer = 0

    def move(self, speed_multiplier):
        pressed_keys = pygame.key.get_pressed()
        move_speed = 5 * speed_multiplier
        if self.active_powerup == "nitro":
            move_speed *= 2

        if self.rect.left > 0 and pressed_keys[K_LEFT]:
            self.rect.move_ip(-move_speed, 0)
        if self.rect.right < SCREEN_WIDTH and pressed_keys[K_RIGHT]:
            self.rect.move_ip(move_speed, 0)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = create_surface(40, 80, RED)
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH-40), -100)
        self.speed = speed

    def move(self, speed_multiplier):
        self.rect.move_ip(0, self.speed * speed_multiplier)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = create_surface(30, 30, YELLOW, shape="circle")
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH-40), -50)

    def move(self, speed):
        self.rect.move_ip(0, speed)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Hazard(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Random hazard: pothole (black) or oil spill (dark gray)
        self.type = random.choice(["pothole", "oil"])
        color = BLACK if self.type == "pothole" else (50, 50, 50)
        self.image = create_surface(50, 50, color, shape="circle")
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH-40), -50)

    def move(self, speed):
        self.rect.move_ip(0, speed)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.type = random.choice(["nitro", "shield", "repair"])
        color = ORANGE if self.type == "nitro" else (CYAN if self.type == "shield" else GREEN)
        self.image = create_surface(30, 30, color)
        # Add a letter for clarity
        font = pygame.font.SysFont("Verdana", 20)
        text = font.render(self.type[0].upper(), True, BLACK)
        self.image.blit(text, (5, 0))
        
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH-40), -50)
        self.spawn_time = time.time()

    def move(self, speed):
        self.rect.move_ip(0, speed)
        if self.rect.top > SCREEN_HEIGHT or time.time() - self.spawn_time > 10:
            self.kill()

def is_overlapping(rect, groups):
    for group in groups:
        for sprite in group:
            if rect.colliderect(sprite.rect):
                return True
    return False

def run_game(screen, player_name):
    settings = load_settings()
    clock = pygame.time.Clock()
    FPS = 60

    base_speed = 3
    if settings["difficulty"] == "easy":
        base_speed = 3
    elif settings["difficulty"] == "hard":
        base_speed = 5

    enemy_speed = 3
    if settings["difficulty"] == "easy":
        enemy_speed = 2.5
    elif settings["difficulty"] == "hard":
        enemy_speed = 3.5

    P1 = Player(settings["car_color"])
    
    enemies = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    hazards = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    
    all_sprites = pygame.sprite.Group()
    all_sprites.add(P1)

    # User Events
    SPAWN_ENEMY = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_ENEMY, 1500)
    
    SPAWN_COIN = pygame.USEREVENT + 2
    pygame.time.set_timer(SPAWN_COIN, 2000)
    
    SPAWN_HAZARD = pygame.USEREVENT + 3
    pygame.time.set_timer(SPAWN_HAZARD, 3000)
    
    SPAWN_POWERUP = pygame.USEREVENT + 4
    pygame.time.set_timer(SPAWN_POWERUP, 10000)

    INC_SPEED = pygame.USEREVENT + 5
    pygame.time.set_timer(INC_SPEED, 5000)

    score = 0
    coins_collected = 0
    distance = 0.0
    bg_y = 0
    speed_multiplier = 1.0

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == INC_SPEED:
                speed_multiplier += 0.05
                
            if event.type == SPAWN_ENEMY:
                e = Enemy(enemy_speed + random.randint(-1, 1))
                if not is_overlapping(e.rect, [enemies, hazards]):
                    enemies.add(e)
                    all_sprites.add(e)
                    
            if event.type == SPAWN_COIN:
                c = Coin()
                if not is_overlapping(c.rect, [enemies, coins, hazards]):
                    coins.add(c)
                    all_sprites.add(c)
                    
            if event.type == SPAWN_HAZARD:
                h = Hazard()
                if not is_overlapping(h.rect, [enemies, hazards]):
                    hazards.add(h)
                    all_sprites.add(h)
                    
            if event.type == SPAWN_POWERUP:
                p = PowerUp()
                if not is_overlapping(p.rect, [powerups, enemies, hazards]):
                    powerups.add(p)
                    all_sprites.add(p)

        # Update Player
        P1.update_powerups(dt)
        P1.move(speed_multiplier)
        
        # Calculate scroll speed
        current_scroll_speed = base_speed * speed_multiplier
        if P1.active_powerup == "nitro":
            current_scroll_speed *= 2

        distance += current_scroll_speed / 10.0
        
        # Move objects
        for entity in all_sprites:
            if entity != P1:
                entity.move(current_scroll_speed)

        # Draw Background
        screen.fill(GRAY)
        bg_y = (bg_y + current_scroll_speed) % 100
        for i in range(-100, SCREEN_HEIGHT + 100, 100):
            pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH//2 - 5, i + bg_y, 10, 50))

        # Check Collisions
        if pygame.sprite.spritecollideany(P1, enemies):
            if P1.active_powerup == "shield" or P1.has_shield:
                P1.active_powerup = None
                P1.has_shield = False
                for e in pygame.sprite.spritecollide(P1, enemies, True):
                    e.kill() # destroy the enemy that hit us
            else:
                running = False

        if pygame.sprite.spritecollideany(P1, hazards):
            if P1.active_powerup == "shield" or P1.has_shield:
                P1.active_powerup = None
                P1.has_shield = False
                for h in pygame.sprite.spritecollide(P1, hazards, True):
                    h.kill()
            else:
                running = False

        collected_coins = pygame.sprite.spritecollide(P1, coins, True)
        for coin in collected_coins:
            coins_collected += 1
            score += 10

        collected_powerups = pygame.sprite.spritecollide(P1, powerups, True)
        for p in collected_powerups:
            if p.type == "nitro":
                P1.active_powerup = "nitro"
                P1.powerup_timer = 5.0
            elif p.type == "shield":
                P1.active_powerup = "shield"
                P1.has_shield = True
                P1.powerup_timer = 0
            elif p.type == "repair":
                # clears all hazards currently on screen
                for h in hazards:
                    h.kill()

        # Score based on distance
        current_score = score + int(distance)

        # Draw sprites
        for entity in all_sprites:
            screen.blit(entity.image, entity.rect)
            if entity == P1 and P1.has_shield:
                # Draw a blue halo if shield is active
                pygame.draw.rect(screen, CYAN, P1.rect, 3, border_radius=5)

        # Draw HUD
        draw_hud(screen, current_score, coins_collected, distance, P1.active_powerup, P1.powerup_timer)

        pygame.display.update()

    # Game Over
    time.sleep(0.5)
    return current_score, int(distance), coins_collected
