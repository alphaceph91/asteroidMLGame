import math

def detect_incoming(spaceship, asteroids, radius):
    """
    Returns a list of asteroids within a circular detection zone of given radius 
    centered on the spaceship.
    """
    detected = []
    spaceship_center = (spaceship.x + spaceship.width / 2, spaceship.y + spaceship.height / 2)
    for asteroid in asteroids:
        asteroid_center = (asteroid.x + asteroid.size / 2, asteroid.y + asteroid.size / 2)
        dist = math.sqrt((spaceship_center[0] - asteroid_center[0])**2 +
                         (spaceship_center[1] - asteroid_center[1])**2)
        if dist <= radius:
            detected.append(asteroid)
    return detected
