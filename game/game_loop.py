import os
import sys
import pygame
import random
from game.spaceship import Spaceship
from game.asteroid import Asteroid

# Suppress libpng warnings
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
os.environ["PYTHONWARNINGS"] = "ignore"

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ML Asteroid Game")

# Load images
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
background_img = pygame.image.load(os.path.join(BASE_DIR, "../images/background.png"))
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
explosion_img = pygame.image.load(os.path.join(BASE_DIR, "../images/explosion.png"))

# Fonts for Game Over text and Score
font = pygame.font.Font(None, 74)
score_font = pygame.font.Font(None, 36)

def show_game_over(score):
    screen.fill((0, 0, 0))  # Clear the screen
    text = font.render("GAME OVER", True, (255, 0, 0))
    score_text = font.render(f"Final Score: {score}", True, (255, 255, 255))
    screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2 - 50))
    screen.blit(score_text, (WIDTH // 2 - 120, HEIGHT // 2 + 20))
    pygame.display.update()
    pygame.time.delay(5000)

def draw_score(score):
    score_text = score_font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

# Game loop function
def run_game():
    running = True
    clock = pygame.time.Clock()
    spaceship = Spaceship(WIDTH, HEIGHT)
    asteroids = [Asteroid(WIDTH, HEIGHT) for _ in range(5)]
    score = 0
    
    # Debugging: print("Entering game loop...")
    
    while running:
        # Debugging: print("Game loop is running...")
        clock.tick(30)
        screen.blit(background_img, (0, 0))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Debugging: print("Quit event detected")
                running = False
        
        spaceship.move()
        spaceship.shoot()
        spaceship.update()
        
        # Move and draw asteroids
        for asteroid in asteroids:
            asteroid.move()
            asteroid.draw(screen)
            
            # Check for collision with spaceship
            if spaceship.get_rect().colliderect(asteroid.get_rect()):
                # Debugging: print("Collision detected! Game Over.")
                show_game_over(score)
                running = False
            
            # Check for missile collision
            for missile in spaceship.missiles:
                if missile.get_rect().colliderect(asteroid.get_rect()):
                    # Debugging: print("Missile hit asteroid!")
                    spaceship.missiles.remove(missile)
                    asteroids.remove(asteroid)
                    
                    # Show explosion effect
                    screen.blit(explosion_img, (asteroid.x, asteroid.y))
                    pygame.display.update()
                    pygame.time.delay(100)
                    
                    asteroids.append(Asteroid(WIDTH, HEIGHT))
                    score += 10  # Increase score when an asteroid is destroyed
                    break
        
        # Draw spaceship
        spaceship.draw(screen)
        
        # Draw score
        draw_score(score)
        
        pygame.display.update()
    
    pygame.quit()

if __name__ == "__main__":
    run_game()