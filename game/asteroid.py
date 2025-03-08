import pygame
import random
import os

# Load asteroid images
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
asteroid_img1 = pygame.image.load(os.path.join(BASE_DIR, "../images/asteroid1.png"))
asteroid_img2 = pygame.image.load(os.path.join(BASE_DIR, "../images/asteroid2.png"))

class Asteroid:
    def __init__(self, width, height):
        self.x = random.randint(0, width)
        self.y = random.randint(-100, -40)
        self.size = random.randint(20, 70)
        # Increase vertical speed range for added challenge
        self.vel_y = random.randint(3, 8)
        # Add horizontal movement with a random direction and speed
        self.vel_x = random.choice([-1, 0, 1]) * random.randint(0, 3)
        self.screen_width = width
        self.screen_height = height
        self.image = pygame.transform.scale(random.choice([asteroid_img1, asteroid_img2]), (self.size, self.size))

    def move(self):
        self.y += self.vel_y
        self.x += self.vel_x
        # Bounce horizontally off the screen edges
        if self.x < 0 or self.x > self.screen_width - self.size:
            self.vel_x = -self.vel_x
        # If the asteroid moves off the bottom, respawn at the top with a new random x-position
        if self.y > self.screen_height:
            self.y = random.randint(-100, -40)
            self.x = random.randint(0, self.screen_width)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)