import pygame
import sys
from ui import main_menu, settings_screen, leaderboard_screen, game_over_screen
from racer import run_game
from persistence import add_score, load_settings

# Initialize pygame globally
pygame.init()
pygame.mixer.init() # Initialize mixer for sound (if used later)

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Racer - Advanced")

    while True:
        # Load settings to check if sound is enabled (can be expanded later for actual BGM)
        settings = load_settings()
        
        # Start at Main Menu
        action, player_name = main_menu(screen)

        if action == "play":
            while True:
                # Run the game loop
                score, distance, coins = run_game(screen, player_name)
                
                # Save the score
                add_score(player_name, score, distance)
                
                # Show Game Over Screen
                go_action = game_over_screen(screen, score, distance, coins)
                if go_action == "menu":
                    break # Break back to main menu
                elif go_action == "retry":
                    continue # Loop back to run_game
                    
        elif action == "leaderboard":
            leaderboard_screen(screen)
            
        elif action == "settings":
            settings_screen(screen)
            
        elif action == "quit":
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    main()
