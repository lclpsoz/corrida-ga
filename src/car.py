import pygame
import time
import math
import numpy as np

class car():
    def __init__(self, fps, x, y, width = 8, height = 16,
                    car_color=(0, 0, 255), front_color=(0, 0, 127)):
        self.frame_time = 1/fps
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.car_color = car_color
        self.front_color = front_color

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

        surface_side = 1.4*max(width, height)
        self.center = [round(surface_side/2), round(surface_side/2)]

        self.points_vertical = [(self.center[0] - self.width/2, self.center[1] - self.height/2),
                                (self.center[0] + self.width/2, self.center[1] - self.height/2),
                                (self.center[0] + self.width/2, self.center[1] + self.height/2),
                                (self.center[0] - self.width/2, self.center[1] + self.height/2) ]
        self.points_horizontal = [  (self.center[0] - self.height/2, self.center[1] - self.width/2),
                                    (self.center[0] + self.height/2, self.center[1] - self.width/2),
                                    (self.center[0] + self.height/2, self.center[1] + self.width/2),
                                    (self.center[0] - self.height/2, self.center[1] + self.width/2) ]
        self.points = self.points_vertical

        self.surface = pygame.Surface((round(surface_side), round(surface_side)))
        self.surface.set_colorkey((0, 255, 0))
        self.surface.fill((0, 255, 0))

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
        self.surface.fill((0, 255, 0))
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

    def get_pos_surface(self):
        """Return position of the surface in the screen."""
        return [round(self.x), round(self.y)]

    def get_pos(self):
        """Return position of the center of the car as a np array."""
        # return np.array([round(self.x), round(self.y)], dtype=np.int) + np.array(self.center, dtype=np.int)
        return np.array(self.get_pos_surface()) + np.array(self.center)

    def get_points(self):
        """Returns position of each point of the car as a list of np array."""
        ret = []
        for pt in self.points:
            ret.append(np.array([self.x, self.y]) + np.array(pt))

        return ret

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