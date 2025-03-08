import pygame
import random
from RLenv import RLenv

# Initialize Pygame
pygame.init()

# Set up the screen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Testing RL Environment")

# Initialize the RL environment
env = RLenv(WIDTH, HEIGHT)

# Reset the environment
state = env.reset()

running = True
clock = pygame.time.Clock()

while running:
    clock.tick(30)
    screen.fill((0, 0, 0))  # Clear screen

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Take a random action (0 = Stay, 1 = Left, 2 = Right, 3 = Up, 4 = Down, 5 = Flip, 6 = Shoot)
    action = random.randint(0, 6)
    state, reward, done = env.step(action)

    # Render environment
    env.render(screen)

    # Print state and reward for debugging
    print(f"Action: {action}, Reward: {reward}, Done: {done}")

    if done:
        print("Game Over! Resetting Environment.")
        state = env.reset()

pygame.quit()