import pygame
import random
from RLenv import RLenv

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Testing RL Environment")

env = RLenv(WIDTH, HEIGHT)

state = env.reset()

running = True
clock = pygame.time.Clock()

while running:
    clock.tick(30)
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    action = random.randint(0, 6)
    state, reward, done = env.step(action)

    env.render(screen)

    print(f"Action: {action}, Reward: {reward}, Done: {done}")

    if done:
        print("Game Over! Resetting Environment.")
        state = env.reset()

pygame.quit()