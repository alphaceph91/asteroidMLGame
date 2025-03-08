import pygame
import numpy as np
import random
import os
import sys
import math
from game.spaceship import Spaceship
from game.asteroid import Asteroid
from utils.detector import detect_incoming

class RLenv:
    def __init__(self, width=800, height=600, debug=True):
        self.width = width
        self.height = height
        self.debug = debug
        self.spaceship = Spaceship(self.width, self.height)
        self.asteroids = [Asteroid(self.width, self.height) for _ in range(10)]
        self.score = 0
        self.lives = 3
        self.done = False
        self.font = pygame.font.Font(None, 36)
        self.asteroids_shot = 0
        # Set detection radius to 200 pixels
        self.detection_radius = 200

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        bg_path = os.path.join(BASE_DIR, "images/background.png")
        self.background_img = pygame.image.load(bg_path)
        self.background_img = pygame.transform.scale(self.background_img, (self.width, self.height))
        
        explosion_path = os.path.join(BASE_DIR, "images/explosion.png")
        self.explosion_img = pygame.image.load(explosion_path)
        self.explosion_img = pygame.transform.scale(self.explosion_img, (50, 50))
        
        heart_path = os.path.join(BASE_DIR, "images/heart.png")
        self.heart_img = pygame.image.load(heart_path)
        self.heart_img = pygame.transform.scale(self.heart_img, (30, 30))
        
        self.explosions = []
    
    def reset(self):
        self.spaceship = Spaceship(self.width, self.height)
        self.asteroids = [Asteroid(self.width, self.height) for _ in range(10)]
        self.score = 0
        self.lives = 3
        self.done = False
        self.explosions = []
        self.asteroids_shot = 0
        return self.get_state()
    
    def get_state(self):
        # Use the closest asteroid for state representation.
        closest = min(self.asteroids, key=lambda ast: abs(ast.x - self.spaceship.x) + abs(ast.y - self.spaceship.y))
        spaceship_center = (self.spaceship.x + self.spaceship.width/2, self.spaceship.y + self.spaceship.height/2)
        asteroid_center = (closest.x + closest.size/2, closest.y + closest.size/2)
        distance = math.sqrt((spaceship_center[0]-asteroid_center[0])**2 +
                             (spaceship_center[1]-asteroid_center[1])**2)
        max_distance = math.sqrt(self.width**2 + self.height**2)
        normalized_distance = distance / max_distance
        # For state reporting, we use a threshold of 150 for collision risk.
        collision_risk = 1 if distance < 150 else 0  
        state = {
            "spaceship_x": self.spaceship.x / self.width,
            "spaceship_y": self.spaceship.y / self.height,
            "asteroid_x": closest.x / self.width,
            "asteroid_y": closest.y / self.height,
            "asteroid_vel": closest.vel_y / 8,  # Assuming max vertical speed is 8
            "missile_ready": 1 if self.spaceship.shoot_cooldown == 0 else 0,
            "lives": self.lives,
            "score": self.score,
            "normalized_distance": normalized_distance,
            "collision_risk": collision_risk
        }
        return state
    
    def get_closest_asteroid(self):
        return min(self.asteroids, key=lambda ast: abs(ast.x - self.spaceship.x) + abs(ast.y - self.spaceship.y))
    
    def step(self, action):
        reward = 0
        print(f"Action Taken: {action}")
        closest = self.get_closest_asteroid()
        spaceship_center = (self.spaceship.x + self.spaceship.width/2, self.spaceship.y + self.spaceship.height/2)
        asteroid_center = (closest.x + closest.size/2, closest.y + closest.size/2)
        old_distance = math.sqrt((spaceship_center[0]-asteroid_center[0])**2 +
                                 (spaceship_center[1]-asteroid_center[1])**2)
        if action == 1:
            self.spaceship.x -= self.spaceship.vel
        elif action == 2:
            self.spaceship.x += self.spaceship.vel
        elif action == 3:
            self.spaceship.y -= self.spaceship.vel
        elif action == 4:
            self.spaceship.y += self.spaceship.vel
        elif action == 5:
            if self.spaceship.shoot_cooldown == 0:
                # Use the detector to see if any asteroid is inside the circle.
                detected = detect_incoming(self.spaceship, self.asteroids, self.detection_radius)
                # Check if the closest asteroid is approaching (vertical speed > 0)
                approaching = 1 if closest.vel_y > 0 else 0
                # Fire as soon as at least one asteroid is detected and the closest is approaching.
                if len(detected) > 0 and approaching:
                    print("Explicit shoot action! (Asteroid detected in circle)")
                    target = min(detected, key=lambda ast: math.sqrt(
                        (spaceship_center[0] - (ast.x+ast.size/2))**2 +
                        (spaceship_center[1] - (ast.y+ast.size/2))**2))
                    self.spaceship.shoot(target)
                    self.spaceship.shoot_cooldown = 10
                    reward += 15
                else:
                    print("Shoot action ignored: no asteroid in detection zone.")
                    reward -= 5
        # Decrease shoot cooldown (ensure it doesn't get negative)
        if self.spaceship.shoot_cooldown > 0:
            self.spaceship.shoot_cooldown -= 1
        self.spaceship.x = max(0, min(self.width - self.spaceship.width, self.spaceship.x))
        self.spaceship.y = max(0, min(self.height - self.spaceship.height, self.spaceship.y))
        new_spaceship_center = (self.spaceship.x + self.spaceship.width/2, self.spaceship.y + self.spaceship.height/2)
        new_distance = math.sqrt((new_spaceship_center[0]-asteroid_center[0])**2 +
                                 (new_spaceship_center[1]-asteroid_center[1])**2)
        if action in [1, 2, 3, 4]:
            if new_distance > old_distance:
                reward += 2 if self.get_state()["collision_risk"] else 1
            else:
                reward -= 1
        for missile in self.spaceship.missiles[:]:
            missile.move()
            # Remove missile if it goes off-screen.
            if missile.x < 0 or missile.x > self.width or missile.y < 0 or missile.y > self.height:
                try:
                    self.spaceship.missiles.remove(missile)
                except ValueError:
                    pass
                continue
            for asteroid in self.asteroids[:]:
                if missile.get_rect().colliderect(asteroid.get_rect()):
                    print("Missile hit an asteroid!")
                    self.explosions.append({'pos': (asteroid.x, asteroid.y), 'timer': 10})
                    try:
                        self.spaceship.missiles.remove(missile)
                    except ValueError:
                        pass
                    self.asteroids.remove(asteroid)
                    self.asteroids.append(Asteroid(self.width, self.height))
                    reward += 10
                    self.score += 10
                    self.asteroids_shot += 1
                    break
        collision_count = 0
        for asteroid in self.asteroids[:]:
            asteroid.move()
            if self.spaceship.get_rect().colliderect(asteroid.get_rect()):
                collision_count += 1
                self.explosions.append({'pos': (self.spaceship.x, self.spaceship.y), 'timer': 10})
                try:
                    self.asteroids.remove(asteroid)
                except ValueError:
                    pass
                self.asteroids.append(Asteroid(self.width, self.height))
        if collision_count > 0:
            self.lives -= collision_count
            reward -= 50 * collision_count
            self.spaceship.x = self.width // 2
            self.spaceship.y = self.height - self.spaceship.height - 10
        if self.lives <= 0:
            self.done = True
        return self.get_state(), reward, self.done
    
    def render(self, screen):
        screen.blit(self.background_img, (0, 0))
        self.spaceship.draw(screen)
        for asteroid in self.asteroids:
            asteroid.draw(screen)
        for missile in self.spaceship.missiles[:]:
            missile.move()
            missile.draw(screen)
        for explosion in self.explosions[:]:
            screen.blit(self.explosion_img, explosion['pos'])
            explosion['timer'] -= 1
            if explosion['timer'] <= 0:
                self.explosions.remove(explosion)
        spaceship_center = (int(self.spaceship.x + self.spaceship.width/2),
                             int(self.spaceship.y + self.spaceship.height/2))
        pygame.draw.circle(screen, (0,255,0), spaceship_center, self.detection_radius, 2)
        detected = detect_incoming(self.spaceship, self.asteroids, self.detection_radius)
        for asteroid in detected:
            asteroid_center = (int(asteroid.x + asteroid.size/2), int(asteroid.y + asteroid.size/2))
            pygame.draw.line(screen, (0,0,255), spaceship_center, asteroid_center, 1)
        color_list = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255),
            (255, 255, 0), (255, 0, 255), (0, 255, 255),
            (128, 0, 128), (255, 165, 0)
        ]
        for i, asteroid in enumerate(self.asteroids):
            asteroid_center = (int(asteroid.x + asteroid.size/2), int(asteroid.y + asteroid.size/2))
            color = color_list[i % len(color_list)]
            pygame.draw.line(screen, color, spaceship_center, asteroid_center, 1)
        if self.debug:
            closest = self.get_closest_asteroid()
            asteroid_center = (int(closest.x+closest.size/2), int(closest.y+closest.size/2))
            pygame.draw.line(screen, (255,0,0), spaceship_center, asteroid_center, 2)
        if not self.done:
            for i in range(self.lives):
                screen.blit(self.heart_img, (10 + i*35, 10))
            score_text = self.font.render(f"Score: {self.score}", True, (255,255,0))
            screen.blit(score_text, (10,50))
            missile_fired_text = self.font.render(f"Missiles Fired: {self.spaceship.missiles_fired}", True, (255,0,255))
            screen.blit(missile_fired_text, (10,90))
            asteroid_counter_text = self.font.render(f"Asteroids Shot: {self.asteroids_shot}", True, (0,255,255))
            screen.blit(asteroid_counter_text, (10,130))
        else:
            game_over_text = self.font.render("GAME OVER", True, (255,0,0))
            final_score_text = self.font.render(f"Final Score: {self.score}", True, (255,255,255))
            screen.blit(game_over_text, (self.width//2-100, self.height//2-50))
            screen.blit(final_score_text, (self.width//2-120, self.height//2+20))
            pygame.display.update()
            pygame.time.delay(3000)
        pygame.display.update()