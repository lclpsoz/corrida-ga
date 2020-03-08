import pygame
import time
import math
import numpy as np

class car():
    def __init__(self, fps, x, y, width = 8, height = 16,
                    car_color=(0, 0, 255), maximum_speed = 35):
        self.frame_time = 1/fps
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.car_color = car_color

        self.EPS = 1e-6

        # The car is 1m x 2m, so, the amount of pixels in it width is a meter.
        self.pixels_per_meter = width

        self.friction_movement = 0.005
        # self.friction_turn_loss_percentage = 0.000
        # Direction is stored as a unit vector
        self.direction = np.asarray([0, 1])
        # Delta per iteration in amount of pixels
        self.delta_pixels = 0  
        # Acceleration in amount of pixels per iteration
        self.acc_pixels = 0.1

        self.points = [(0, 0), (self.width, 0), (self.width, self.height), (0, self.height)]
        self.points_vertical = [(0, 0), (self.width, 0), (self.width, self.height), (0, self.height)]
        self.points_horizontal = [(0, 0), (self.height, 0), (self.height, self.width), (0, self.width)]
        self.center = [self.height/2, self.width/2]

        self.surface = pygame.Surface((100, 100))
        self.surface.fill((255, 255, 255))

    def handle_keys(self):
        """Do action based on pressed key."""
        key = pygame.key.get_pressed()
        turn_angle = max(1.5, (11 - self.delta_pixels)/2)
        if key[pygame.K_LEFT]:
            if(self.delta_pixels > self.EPS):
                self.direction = self.rotate_degree((0, 0), self.direction, -turn_angle)
                # self.delta_pixels *= 1-self.friction_turn_loss_percentage
        if key[pygame.K_RIGHT]:
            if(self.delta_pixels > self.EPS):
                self.direction = self.rotate_degree((0, 0), self.direction, turn_angle)
                # self.delta_pixels *= 1-self.friction_turn_loss_percentage
        if key[pygame.K_UP]:
            self.delta_pixels += self.acc_pixels

        # Breaking
        if key[pygame.K_DOWN]:
            self.delta_pixels = max(0, self.delta_pixels-1.5*self.acc_pixels)

        # Change car graphic by speed vector direction
        if(self.delta_pixels > self.EPS):
            if(abs(self.direction[0]) > abs(self.direction[1])):
                self.points = self.points_horizontal
            else:
                self.points = self.points_vertical

        # Apply movement
        self.x += self.direction[0]*self.delta_pixels
        self.y += self.direction[1]*self.delta_pixels

        # Apply friction
        self.delta_pixels *= 1 - self.friction_movement

    def draw(self):
        """Updates surface based on changes in the car shape."""
        self.surface.fill((255, 255, 255))
        pygame.draw.polygon(self.surface, self.car_color, self.points)
        return self.surface

    def rotate_degree(self, origin, point, angle):
        """
        Rotate a point counterclockwise by a given angle around a given origin.

        The angle should be given in degrees.
        """
        return self.rotate(origin, point, (angle*math.pi)/180)

    def rotate(self, origin, point, angle):
        """
        Rotate a point counterclockwise by a given angle around a given origin.

        The angle should be given in radians.
        """
        ox, oy = origin
        px, py = point

        qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
        qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
        return np.asarray([qx, qy])

    def vector_magnitude_sum(self, vector, scalar):
        """Sum scalar value to vector magnitude."""
        vector = np.asarray(vector)
        x, y = vector
        vector_magnitude = math.sqrt(x**2 + y**2)
        if vector_magnitude > 0:
            vector_unit = vector/vector_magnitude
        else:
            vector_unit = [1, 0]
        return vector + (vector_unit*scalar)


    def get_pos(self):
        """Return position of player as a tuple of ints."""
        return (int(round(self.x)), int(round(self.y)))

    def get_speed_squared(self):
        """Returns the speed of the car in meters per second squared."""
        return self.delta_pixels/self.frame_time
    
    def get_speed(self):
        """Returns the speed of the car in meters per second."""
        return math.sqrt(self.get_speed_squared())

    @staticmethod
    def get_controls():
        """Returns multiple strings with manual controls information."""
        return ["Arrow up: Accelerate the car forward.",
                "Arrow down: Breaks.",
                "Arrows to sides: Change the car direction."]