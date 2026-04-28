import pygame
import sys
from persistence import load_settings, save_settings, load_leaderboard

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 215, 0)

pygame.font.init()
FONT_LARGE = pygame.font.SysFont("Verdana", 50)
FONT_MEDIUM = pygame.font.SysFont("Verdana", 30)
FONT_SMALL = pygame.font.SysFont("Verdana", 20)

def draw_text(surface, text, font, color, x, y, center=False):
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(text_surface, rect)

class Button:
    def __init__(self, x, y, w, h, text, color, hover_color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=5)
        draw_text(surface, self.text, FONT_MEDIUM, BLACK, self.rect.centerx, self.rect.centery, center=True)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered

def username_screen(screen):
    clock = pygame.time.Clock()
    name = ""
    input_rect = pygame.Rect(100, 250, 200, 40)
    active = True

    while True:
        screen.fill(WHITE)
        draw_text(screen, "Enter Username:", FONT_MEDIUM, BLACK, 200, 200, center=True)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return name if name else "Player"
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 10 and event.unicode.isprintable():
                        name += event.unicode
        
        # Draw input box
        pygame.draw.rect(screen, GRAY, input_rect)
        pygame.draw.rect(screen, BLACK, input_rect, 2)
        draw_text(screen, name, FONT_MEDIUM, BLACK, input_rect.x + 5, input_rect.y + 2)
        draw_text(screen, "Press Enter to Start", FONT_SMALL, DARK_GRAY, 200, 320, center=True)

        pygame.display.flip()
        clock.tick(60)

def main_menu(screen):
    clock = pygame.time.Clock()
    buttons = [
        Button(100, 200, 200, 50, "Play", GRAY, WHITE),
        Button(100, 270, 200, 50, "Leaderboard", GRAY, WHITE),
        Button(100, 340, 200, 50, "Settings", GRAY, WHITE),
        Button(100, 410, 200, 50, "Quit", GRAY, WHITE)
    ]

    while True:
        screen.fill(DARK_GRAY)
        draw_text(screen, "RACER", FONT_LARGE, WHITE, 200, 100, center=True)
        
        mouse_pos = pygame.mouse.get_pos()
        for btn in buttons:
            btn.check_hover(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for btn in buttons:
                    if btn.is_hovered:
                        if btn.text == "Play":
                            name = username_screen(screen)
                            return "play", name
                        return btn.text.lower(), None

        for btn in buttons:
            btn.draw(screen)

        pygame.display.flip()
        clock.tick(60)

def settings_screen(screen):
    clock = pygame.time.Clock()
    settings = load_settings()
    
    colors = ["blue", "red", "green", "yellow"]
    difficulties = ["easy", "normal", "hard"]

    btn_back = Button(100, 500, 200, 50, "Back", GRAY, WHITE)
    
    while True:
        screen.fill(DARK_GRAY)
        draw_text(screen, "Settings", FONT_LARGE, WHITE, 200, 80, center=True)

        mouse_pos = pygame.mouse.get_pos()
        btn_back.check_hover(mouse_pos)

        # Draw toggles (simple clickable areas for now)
        sound_text = f"Sound: {'ON' if settings['sound'] else 'OFF'}"
        color_text = f"Car Color: {settings['car_color'].upper()}"
        diff_text = f"Difficulty: {settings['difficulty'].upper()}"

        btn_sound = Button(50, 180, 300, 50, sound_text, GRAY, WHITE)
        btn_color = Button(50, 260, 300, 50, color_text, GRAY, WHITE)
        btn_diff = Button(50, 340, 300, 50, diff_text, GRAY, WHITE)

        buttons = [btn_sound, btn_color, btn_diff, btn_back]
        for btn in buttons:
            btn.check_hover(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_settings(settings)
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_sound.is_hovered:
                    settings["sound"] = not settings["sound"]
                elif btn_color.is_hovered:
                    idx = colors.index(settings["car_color"])
                    settings["car_color"] = colors[(idx + 1) % len(colors)]
                elif btn_diff.is_hovered:
                    idx = difficulties.index(settings["difficulty"])
                    settings["difficulty"] = difficulties[(idx + 1) % len(difficulties)]
                elif btn_back.is_hovered:
                    save_settings(settings)
                    return

        for btn in buttons:
            btn.draw(screen)

        pygame.display.flip()
        clock.tick(60)

def leaderboard_screen(screen):
    clock = pygame.time.Clock()
    scores = load_leaderboard()
    btn_back = Button(100, 520, 200, 50, "Back", GRAY, WHITE)

    while True:
        screen.fill(DARK_GRAY)
        draw_text(screen, "Top 10 Scores", FONT_LARGE, WHITE, 200, 50, center=True)

        y = 120
        draw_text(screen, "Rank  Name      Score   Dist", FONT_SMALL, YELLOW, 20, y)
        y += 30
        for i, s in enumerate(scores):
            text = f"{i+1:2d}.   {s['name'][:8]:<8}  {s['score']:<6}  {s['distance']}"
            draw_text(screen, text, FONT_SMALL, WHITE, 20, y)
            y += 30

        mouse_pos = pygame.mouse.get_pos()
        btn_back.check_hover(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_back.is_hovered:
                    return

        btn_back.draw(screen)
        pygame.display.flip()
        clock.tick(60)

def game_over_screen(screen, score, distance, coins):
    clock = pygame.time.Clock()
    btn_retry = Button(100, 350, 200, 50, "Retry", GRAY, WHITE)
    btn_menu = Button(100, 420, 200, 50, "Main Menu", GRAY, WHITE)

    while True:
        screen.fill(RED)
        draw_text(screen, "GAME OVER", FONT_LARGE, BLACK, 200, 100, center=True)
        
        draw_text(screen, f"Score: {score}", FONT_MEDIUM, WHITE, 200, 180, center=True)
        draw_text(screen, f"Distance: {distance}m", FONT_MEDIUM, WHITE, 200, 220, center=True)
        draw_text(screen, f"Coins: {coins}", FONT_MEDIUM, WHITE, 200, 260, center=True)

        mouse_pos = pygame.mouse.get_pos()
        btn_retry.check_hover(mouse_pos)
        btn_menu.check_hover(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_retry.is_hovered:
                    return "retry"
                if btn_menu.is_hovered:
                    return "menu"

        btn_retry.draw(screen)
        btn_menu.draw(screen)

        pygame.display.flip()
        clock.tick(60)

def draw_hud(screen, score, coins, distance, active_powerup, powerup_time):
    draw_text(screen, f"Score: {score}", FONT_SMALL, BLACK, 10, 10)
    draw_text(screen, f"Coins: {coins}", FONT_SMALL, BLACK, 10, 35)
    draw_text(screen, f"Dist: {int(distance)}m", FONT_SMALL, BLACK, 10, 60)

    if active_powerup:
        text = f"{active_powerup.upper()}"
        if powerup_time > 0:
            text += f" ({powerup_time:.1f}s)"
        color = BLUE if active_powerup == "shield" else (YELLOW if active_powerup == "nitro" else GREEN)
        draw_text(screen, text, FONT_SMALL, color, 400 - 10, 10, center=False)
        # To align right, recalculate rect
        text_surf = FONT_SMALL.render(text, True, color)
        rect = text_surf.get_rect()
        rect.topright = (390, 10)
        screen.blit(text_surf, rect)
