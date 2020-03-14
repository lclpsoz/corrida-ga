import pygame
import math
import numpy as np
from circuit import Circuit
import time

class CircuitCircle(Circuit):
    def __init__(self, config):
        super(CircuitCircle, self).__init__(config)
        self.center = np.asarray(config['center'])
        self.inner_circle = config['inner_circle']
        self.outter_circle = config['outter_circle']
        self.surface = pygame.Surface((config['width'], config['height']))
        self.start = np.asarray([self.center[0] - (self.outter_circle + self.inner_circle) // 2,
                                    self.center[1]])
        self.num_of_sectors = 36
    
    def draw(self):
        """Returns the pygame.Surface with the track drawed"""
        self.surface.set_colorkey((0, 255, 0))
        self.surface.fill((0,255,0))
        pygame.draw.circle(self.surface, self.color_background, self.center,
                            self.outter_circle)    
        pygame.draw.circle(self.surface, self.color_slow_area, self.center,
                            self.outter_circle - self.wall)
        pygame.draw.circle(self.surface, self.color_wall, self.center,
                            self.outter_circle - self.slow_area - self.wall)    
        pygame.draw.circle(self.surface, self.color_slow_area, self.center,
                            self.inner_circle + self.slow_area)    
        pygame.draw.circle(self.surface, self.color_background, self.center,
                            self.inner_circle)    
        pygame.draw.circle(self.surface, self.color_wall, self.center,
                            self.inner_circle - self.wall)    
        return self.surface

    def reset(self, car_id):
        self.car_sectors[car_id] = [0 for i in range(self.num_of_sectors)]
        self.car_sectors[car_id][0] = 1
        self.car_current_sector[car_id] = 0
        self.car_start_time[car_id] = time.time()

    def collision(self, shape):
        """Returns the type of collision of the shapely shape and the circuit.
        Can be NONE, SLOW_AREA or WALL."""
        points = self.get_points_shape(shape)
        c = Circuit.COLLISION_NONE
        for p in points:
            d = math.hypot(self.center[0] - p[0], self.center[1] - p[1])
            if d <= self.inner_circle or d >= self.outter_circle - self.wall:
                return Circuit.COLLISION_WALL
            elif(d <= self.inner_circle + self.slow_area or
                d >= self.outter_circle - self.slow_area):
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