import pygame
import os
import math

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
missile_img_orig = pygame.image.load(os.path.join(BASE_DIR, "../images/missile.png"))
missile_img_orig = pygame.transform.scale(missile_img_orig, (10, 20))

class Missile:
    def __init__(self, x, y, target=None, speed=10):
        self.x = x
        self.y = y
        self.speed = speed
        self.target = target
        if self.target is not None:
            self.update_direction()
        else:
            self.vel_x = 0
            self.vel_y = -speed

    def update_direction(self):
        dx = (self.target.x + self.target.size / 2) - self.x
        dy = (self.target.y + self.target.size / 2) - self.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist != 0:
            self.vel_x = self.speed * dx / dist
            self.vel_y = self.speed * dy / dist
        else:
            self.vel_x = 0
            self.vel_y = -self.speed

    def move(self):
        if self.target is not None:
            self.update_direction()
        self.x += self.vel_x
        self.y += self.vel_y

    def draw(self, screen):
        #computing the angle (in degrees) from the velocity vector
        #Pygame's coordinate system has y increasing downward
        angle = math.degrees(math.atan2(-self.vel_y, self.vel_x))
        #adjusting the angle by subtracting 90 degrees so that an image originally pointing upward rotates correctly
        adjusted_angle = angle - 90
        rotated_img = pygame.transform.rotate(missile_img_orig, adjusted_angle)
        #Get the rect of the rotated image with its center at the missile's center
        rect = rotated_img.get_rect(center=(self.x + 5, self.y + 10))
        screen.blit(rotated_img, rect.topleft)

    def get_rect(self):
        #creating a rect based on current x,y and missile size
        return pygame.Rect(self.x, self.y, 10, 20)