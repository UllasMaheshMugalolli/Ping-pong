import pygame
from game.game_engine import GameEngine
# Initialize pygame/Start application
pygame.init()
# Screen dimensions
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ping Pong - Pygame Version")
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
# Clock
clock = pygame.time.Clock()
FPS = 60
def main():
    """Main game loop with game over and replay functionality."""
    game_active = True
    engine = GameEngine(WIDTH, HEIGHT)
    while game_active:
        running = True
        game_over = False
        # Main game loop
        while running and not game_over:
            SCREEN.fill(BLACK)   
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    game_active = False
            if game_active:
                # Game logic
                engine.handle_input()
                engine.update()
                engine.render(SCREEN)    
                # Check if game is over
                if engine.player_score >= engine.max_score or engine.ai_score >= engine.max_score:
                    game_over = True
                
                pygame.display.flip()
                clock.tick(FPS)
        # Game over sequence
        if game_over:
            # Display winner
            winner = "Player" if engine.player_score >= engine.max_score else "AI"
            SCREEN.fill(BLACK)
            text_surface = engine.font.render(f"{winner} Wins!", True, WHITE)
            SCREEN.blit(
                text_surface,
                (WIDTH // 2 - text_surface.get_width() // 2,
                 HEIGHT // 2 - text_surface.get_height() // 2)
            )
            pygame.display.flip()
            pygame.time.delay(2000)
            # Show replay menu
            choice = engine.show_replay_menu(SCREEN)
            if choice == "exit":
                game_active = False
            else:
                # Reset for new game
                engine.max_score = (choice // 2) + 1
                engine.player_score = 0
                engine.ai_score = 0
                engine.ball.reset()
    pygame.quit()
if __name__ == "__main__":
    main()