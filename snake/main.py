import sys
import pygame
from config import *
import db
from game import run_game

# Initialize pygame
pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Advanced Snake")
clock = pygame.time.Clock()

# Database init
db.init_db()

def draw_text(text, font, color, surface, x, y, center=True):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    if center:
        textrect.center = (x, y)
    else:
        textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def draw_button(text, font, rect, surface, mouse_pos):
    color = UI_BTN_HOVER if rect.collidepoint(mouse_pos) else UI_BTN
    pygame.draw.rect(surface, color, rect, border_radius=8)
    draw_text(text, font, UI_TEXT, surface, rect.centerx, rect.centery)

def main_menu():
    username = ""
    active = False
    
    input_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 200, 200, 40)
    color_active = pygame.Color('lightskyblue3')
    color_passive = pygame.Color('chartreuse4')
    
    play_btn = pygame.Rect(SCREEN_WIDTH//2 - 100, 280, 200, 50)
    lb_btn = pygame.Rect(SCREEN_WIDTH//2 - 100, 350, 200, 50)
    sett_btn = pygame.Rect(SCREEN_WIDTH//2 - 100, 420, 200, 50)
    quit_btn = pygame.Rect(SCREEN_WIDTH//2 - 100, 490, 200, 50)

    while True:
        screen.fill(UI_BG)
        mouse_pos = pygame.mouse.get_pos()
        
        draw_text("Advanced Snake", FONT_LARGE, WHITE, screen, SCREEN_WIDTH//2, 100)
        draw_text("Enter Username:", FONT_SMALL, WHITE, screen, SCREEN_WIDTH//2, 170)
        
        color = color_active if active else color_passive
        pygame.draw.rect(screen, color, input_rect, 2)
        draw_text(username, FONT_SMALL, WHITE, screen, input_rect.centerx, input_rect.centery)
        
        draw_button("Play", FONT_MEDIUM, play_btn, screen, mouse_pos)
        draw_button("Leaderboard", FONT_MEDIUM, lb_btn, screen, mouse_pos)
        draw_button("Settings", FONT_MEDIUM, sett_btn, screen, mouse_pos)
        draw_button("Quit", FONT_MEDIUM, quit_btn, screen, mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(event.pos):
                    active = True
                else:
                    active = False
                    
                if play_btn.collidepoint(event.pos):
                    if not username.strip():
                        username = "Player"
                    return "play", username
                elif lb_btn.collidepoint(event.pos):
                    return "leaderboard", ""
                elif sett_btn.collidepoint(event.pos):
                    return "settings", ""
                elif quit_btn.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
                    
            if event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_RETURN:
                    pass
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    if len(username) < 15:
                        username += event.unicode
                        
        pygame.display.flip()
        clock.tick(30)

def leaderboard_screen():
    back_btn = pygame.Rect(SCREEN_WIDTH//2 - 100, 500, 200, 50)
    scores = db.get_top_scores()
    
    while True:
        screen.fill(UI_BG)
        mouse_pos = pygame.mouse.get_pos()
        
        draw_text("Leaderboard - Top 10", FONT_LARGE, WHITE, screen, SCREEN_WIDTH//2, 80)
        
        y_offset = 150
        draw_text(f"{'Rank':<5} {'Username':<15} {'Score':<6} {'Level':<6} {'Date'}", FONT_SMALL, WHITE, screen, SCREEN_WIDTH//2 - 200, y_offset, center=False)
        pygame.draw.line(screen, WHITE, (SCREEN_WIDTH//2 - 200, y_offset + 30), (SCREEN_WIDTH//2 + 300, y_offset + 30))
        y_offset += 40
        
        for idx, row in enumerate(scores):
            # row: username, score, level_reached, played_at
            date_str = row[3].strftime("%Y-%m-%d")
            text = f"{idx+1:<5} {row[0]:<15} {row[1]:<6} {row[2]:<6} {date_str}"
            draw_text(text, FONT_SMALL, WHITE, screen, SCREEN_WIDTH//2 - 200, y_offset, center=False)
            y_offset += 30
            
        draw_button("Back", FONT_MEDIUM, back_btn, screen, mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.collidepoint(event.pos):
                    return
                    
        pygame.display.flip()
        clock.tick(30)

def settings_screen():
    settings = load_settings()
    back_btn = pygame.Rect(SCREEN_WIDTH//2 - 100, 500, 200, 50)
    
    grid_rect = pygame.Rect(SCREEN_WIDTH//2 + 50, 200, 50, 30)
    sound_rect = pygame.Rect(SCREEN_WIDTH//2 + 50, 260, 50, 30)
    
    colors = [GREEN, RED, BLUE, (255, 255, 0), (255, 0, 255)]
    color_rects = []
    start_x = SCREEN_WIDTH//2 - 50
    for i in range(len(colors)):
        color_rects.append(pygame.Rect(start_x + i * 40, 320, 30, 30))
        
    while True:
        screen.fill(UI_BG)
        mouse_pos = pygame.mouse.get_pos()
        
        draw_text("Settings", FONT_LARGE, WHITE, screen, SCREEN_WIDTH//2, 100)
        
        draw_text("Grid Overlay:", FONT_MEDIUM, WHITE, screen, SCREEN_WIDTH//2 - 100, 215)
        grid_color = GREEN if settings["grid_overlay"] else RED
        pygame.draw.rect(screen, grid_color, grid_rect)
        draw_text("ON" if settings["grid_overlay"] else "OFF", FONT_SMALL, WHITE, screen, grid_rect.centerx, grid_rect.centery)
        
        draw_text("Sound:", FONT_MEDIUM, WHITE, screen, SCREEN_WIDTH//2 - 100, 275)
        sound_color = GREEN if settings["sound"] else RED
        pygame.draw.rect(screen, sound_color, sound_rect)
        draw_text("ON" if settings["sound"] else "OFF", FONT_SMALL, WHITE, screen, sound_rect.centerx, sound_rect.centery)
        
        draw_text("Snake Color:", FONT_MEDIUM, WHITE, screen, SCREEN_WIDTH//2 - 150, 335)
        for i, c_rect in enumerate(color_rects):
            c = colors[i]
            pygame.draw.rect(screen, c, c_rect)
            # Highlight selected
            if tuple(settings["snake_color"]) == tuple(c):
                pygame.draw.rect(screen, WHITE, c_rect, 3)
                
        draw_button("Save & Back", FONT_MEDIUM, back_btn, screen, mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if grid_rect.collidepoint(event.pos):
                    settings["grid_overlay"] = not settings["grid_overlay"]
                if sound_rect.collidepoint(event.pos):
                    settings["sound"] = not settings["sound"]
                for i, c_rect in enumerate(color_rects):
                    if c_rect.collidepoint(event.pos):
                        settings["snake_color"] = list(colors[i])
                if back_btn.collidepoint(event.pos):
                    save_settings(settings)
                    return
                    
        pygame.display.flip()
        clock.tick(30)

def game_over_screen(score, level, personal_best):
    retry_btn = pygame.Rect(SCREEN_WIDTH//2 - 110, 400, 100, 50)
    menu_btn = pygame.Rect(SCREEN_WIDTH//2 + 10, 400, 100, 50)
    
    while True:
        screen.fill(UI_BG)
        mouse_pos = pygame.mouse.get_pos()
        
        draw_text("GAME OVER", FONT_LARGE, RED, screen, SCREEN_WIDTH//2, 150)
        
        draw_text(f"Final Score: {score}", FONT_MEDIUM, WHITE, screen, SCREEN_WIDTH//2, 230)
        draw_text(f"Level Reached: {level}", FONT_MEDIUM, WHITE, screen, SCREEN_WIDTH//2, 280)
        draw_text(f"Personal Best: {personal_best}", FONT_MEDIUM, WHITE, screen, SCREEN_WIDTH//2, 330)
        
        draw_button("Retry", FONT_MEDIUM, retry_btn, screen, mouse_pos)
        draw_button("Menu", FONT_MEDIUM, menu_btn, screen, mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_btn.collidepoint(event.pos):
                    return "retry"
                elif menu_btn.collidepoint(event.pos):
                    return "menu"
                    
        pygame.display.flip()
        clock.tick(30)

def main():
    while True:
        action, username = main_menu()
        
        if action == "play":
            while True:
                personal_best = db.get_personal_best(username)
                score, level, reason = run_game(screen, username, personal_best, clock)
                
                if reason == "quit":
                    pygame.quit()
                    sys.exit()
                    
                # Game over
                db.save_score(username, score, level)
                # Update personal best for display on game over screen
                personal_best = max(score, personal_best)
                
                go_action = game_over_screen(score, level, personal_best)
                if go_action == "menu":
                    break
        elif action == "leaderboard":
            leaderboard_screen()
        elif action == "settings":
            settings_screen()

if __name__ == "__main__":
    main()
