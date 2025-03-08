import pygame
import random
import os

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ML Asteroid Game")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

spaceship_img = pygame.image.load(os.path.join(BASE_DIR, "images/spaceship2.png"))
spaceship_img = pygame.transform.scale(spaceship_img, (50, 50))
asteroid_img1 = pygame.image.load(os.path.join(BASE_DIR, "images/asteroid1.png"))
asteroid_img2 = pygame.image.load(os.path.join(BASE_DIR, "images/asteroid2.png"))
background_img = pygame.image.load(os.path.join(BASE_DIR, "images/background.png"))
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
missile_img = pygame.image.load(os.path.join(BASE_DIR, "images/missile.png"))
missile_img = pygame.transform.scale(missile_img, (10, 20))
explosion_img = pygame.image.load(os.path.join(BASE_DIR, "images/explosion.png"))

font = pygame.font.Font(None, 74)

def show_game_over():
    text = font.render("GAME OVER", True, RED)
    screen.blit(text, (WIDTH // 2 - 150, HEIGHT // 2 - 50))
    pygame.display.update()
    pygame.time.delay(2000)

#SPACESHIP
class Spaceship:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 70
        self.width = 50
        self.height = 50
        self.vel = 5
        self.missiles = []
        self.shoot_cooldown = 0

    def move(self):
        self.x += random.choice([-1, 1]) * self.vel
        self.x = max(0, min(WIDTH - self.width, self.x))

    def shoot(self):
        if self.shoot_cooldown == 0:
            self.missiles.append(Missile(self.x + self.width // 2 - 5, self.y))
            self.shoot_cooldown = 10  # Cooldown time to prevent constant firing

    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def draw(self):
        screen.blit(spaceship_img, (self.x, self.y))
        for missile in self.missiles:
            missile.move()
            missile.draw()

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

#MISSILE
class Missile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel = -10

    def move(self):
        self.y += self.vel

    def draw(self):
        screen.blit(missile_img, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, 10, 20)

#ASTEROID
class Asteroid:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-100, -40)
        self.size = random.randint(20, 70)
        self.vel = random.randint(2, 5)
        self.image = pygame.transform.scale(random.choice([asteroid_img1, asteroid_img2]), (self.size, self.size))

    def move(self):
        self.y += self.vel
        if self.y > HEIGHT:
            self.y = random.randint(-100, -40)
            self.x = random.randint(0, WIDTH)

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

#GAME LOOP
running = True
clock = pygame.time.Clock()
spaceship = Spaceship()
asteroids = [Asteroid() for _ in range(5)]

while running:
    clock.tick(30)
    screen.blit(background_img, (0, 0))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    spaceship.move()
    spaceship.shoot()
    spaceship.update()

    for asteroid in asteroids:
        asteroid.move()
        asteroid.draw()
        
        if spaceship.get_rect().colliderect(asteroid.get_rect()):
            show_game_over()
            running = False
        
        for missile in spaceship.missiles:
            if missile.get_rect().colliderect(asteroid.get_rect()):
                screen.blit(explosion_img, (asteroid.x, asteroid.y))
                spaceship.missiles.remove(missile)
                asteroids.remove(asteroid)
                asteroids.append(Asteroid())
                break
    
    spaceship.draw()
    
    pygame.display.update()

pygame.quit()