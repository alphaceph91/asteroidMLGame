import pygame
import os
import random
from game.missile import Missile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
spaceship_img = pygame.image.load(os.path.join(BASE_DIR, "../images/spaceship.png"))
spaceship_img = pygame.transform.scale(spaceship_img, (50, 50))

class Spaceship:
    def __init__(self, width, height):
        self.x = width // 2
        self.y = height - 70
        self.width = 50
        self.height = 50
        self.vel = 5
        self.missiles = []
        self.shoot_cooldown = 0
        self.screen_width = width
        self.screen_height = height
        self.missiles_fired = 0

    def move(self):
        self.x += random.choice([-1, 1]) * self.vel
        self.x = max(0, min(self.screen_width - self.width, self.x))

    def shoot(self, target=None):
        missile_x = self.x + self.width // 2 - 5
        missile_y = self.y
        self.missiles.append(Missile(missile_x, missile_y, target))
        self.shoot_cooldown = 10
        self.missiles_fired += 1

    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def draw(self, screen):
        screen.blit(spaceship_img, (self.x, self.y))
        for missile in self.missiles:
            missile.move()
            missile.draw(screen)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)