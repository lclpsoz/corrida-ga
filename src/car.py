import pygame
import time

class car():
    def __init__(self, width = 16, height = 32, x = 64, y = 54, car_color=(0, 0, 255)):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.car_color = car_color

        self.dx = 0
        self.dy = 0
        self.ddx = 0.1
        self.ddy = 0.1

        self.points = [(0, 0), (self.width, 0), (self.width, self.height), (0, self.height)]
        self.points_vertical = [(0, 0), (self.width, 0), (self.width, self.height), (0, self.height)]
        self.points_horizontal = [(0, 0), (self.height, 0), (self.height, self.width), (0, self.width)]
        self.center = [self.height/2, self.width/2]

        self.surface = pygame.Surface((100, 100))
        self.surface.fill((255, 255, 255))

    def handle_keys(self):
        """Do action based on pressed key."""
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            self.dx -= self.ddx
        if key[pygame.K_RIGHT]:
            self.dx += self.ddx
        if key[pygame.K_UP]:
            self.dy -= self.ddy
        if key[pygame.K_DOWN]:
            self.dy += self.ddy

        # Breaking
        if key[pygame.K_SPACE]:
            if self.dy < 0:
                self.dy = min(0, self.dy + 3*self.ddy)
            else:
                self.dy = max(0, self.dy - 3*self.ddy)
            if self.dx < 0:
                self.dx = min(0, self.dx + 3*self.ddx)
            else:
                self.dx = max(0, self.dx - 3*self.ddx)

        # Change car direction
        if(abs(self.dx) > abs(self.dy)):
            self.points = self.points_horizontal
        else:
            self.points = self.points_vertical

        # Apply movement
        self.x += self.dx
        self.y += self.dy

    def draw(self):
        """Updates surface based on changes in the car shape."""
        self.surface.fill((255, 255, 255))
        pygame.draw.polygon(self.surface, self.car_color, self.points)
        return self.surface

    def get_pos(self):
        """Return position of player as a tuple of ints."""
        return (int(round(self.x)), int(round(self.y)))

    @staticmethod
    def get_controls():
        """Returns multiple strings with manual controls information."""
        return ["Arrows: Accelerate the car in that direction.",
                "Space: Breaks."]