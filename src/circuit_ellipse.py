import pygame
import math
import numpy as np
from circuit import Circuit
import time

class CircuitEllipse(Circuit):
    def __init__(self, config):
        super(CircuitEllipse, self).__init__(config)
        self.center = np.asarray(config['center'])
        self.inner = config['inner']
        self.outter = config['outter']
        self.surface = pygame.Surface((config['width'], config['height']))
        self.start = np.asarray([self.center[0] - (self.outter[0] + self.inner[0]) // 2,
                                    self.center[1]])
        self.num_of_sectors = 36
    
    def draw(self):
        """Returns the pygame.Surface with the track drawed"""
        self.surface.set_colorkey((0, 255, 0))
        self.surface.fill((0,255,0))
        pygame.draw.ellipse(self.surface, self.color_background, 
                            (self.center[0] - self.outter[0], self.center[1] - self.outter[1],
                            2 * self.outter[0], 2 * self.outter[1]))    
        pygame.draw.ellipse(self.surface, self.color_slow_area,
                            (self.center[0] - self.outter[0] + self.wall, self.center[1] - self.outter[1] + self.wall, 
                            2 * (self.outter[0] - self.wall), 2 * (self.outter[1] - self.wall)))
        pygame.draw.ellipse(self.surface, self.color_wall,
                            (self.center[0] - self.outter[0] + self.slow_area + self.wall, self.center[1] - self.outter[1] + self.slow_area + self.wall, 
                            2 * (self.outter[0] - self.slow_area - self.wall), 2 * (self.outter[1] - self.slow_area - self.wall)))
        pygame.draw.ellipse(self.surface, self.color_slow_area,
                            (self.center[0] - self.inner[0] - self.slow_area, self.center[1] - self.inner[1] - self.slow_area,
                            2 * (self.inner[0] + self.slow_area), 2 * (self.inner[1] + self.slow_area)))
        pygame.draw.ellipse(self.surface, self.color_background,
                            (self.center[0] - self.inner[0], self.center[1] - self.inner[1],
                            2 * self.inner[0], 2 * self.inner[1]))
        pygame.draw.ellipse(self.surface, self.color_wall,
                            (self.center[0] - self.inner[0] + self.wall, self.center[1] - self.inner[1] + self.wall,
                            2 * (self.inner[0] - self.wall), 2 * (self.inner[1] - self.wall)))
        return self.surface

    def collision(self, shape):
        """Returns the type of collision of the shapely shape and the circuit.
        Can be NONE, SLOW_AREA or WALL."""
        points = self.get_points_shape(shape)
        c = Circuit.COLLISION_NONE
        for p in points:
            d = math.hypot(self.center[0] - p[0], self.center[1] - p[1])
            theta = math.atan2(-(p[1] - self.center[1]), p[0] - self.center[0])
            r1 = self.outter[0] * self.outter[1] / math.sqrt(self.outter[0] * self.outter[0] * math.sin(theta) * math.sin(theta) + 
                                self.outter[1] * self.outter[1] * math.cos(theta) * math.cos(theta))
            r2 = self.inner[0] * self.inner[1] / math.sqrt(self.inner[0] * self.inner[0] * math.sin(theta) * math.sin(theta) + 
                                self.inner[1] * self.inner[1] * math.cos(theta) * math.cos(theta))
            if d >= r1 - self.wall or d <= r2:
                return Circuit.COLLISION_WALL
            elif(d <= r2 + self.slow_area or
                d >= r1 - self.slow_area):
                c = Circuit.COLLISION_SLOW_AREA
        return c

    def cur_sector(self, point):
        """Returns the sector of a point"""
        angle = math.atan2(-(point[1] - self.center[1]), point[0] - self.center[0])
        angle = math.degrees(angle)
        angle = 180 - angle
        if angle < 0:
            angle += 360
        return int(angle // 10)

    def update_car_sector(self, car_id, player):
        """Updates the sector of the car (maximum sector of all its points)"""
        now = -1
        for p in player.get_points():
            now = max(now, self.cur_sector(p))

        if ((self.car_current_sector[car_id] + 1) % self.num_of_sectors == now) and\
                (self.car_sectors[car_id][self.car_current_sector[car_id]] == 1):
            self.car_sectors[car_id][now] = 1

        self.car_current_sector[car_id] = now