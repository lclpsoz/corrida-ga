import pygame
import math
from shapely.geometry.polygon import Polygon
from shapely.geometry import LineString
import time

from circuit.circuit import Circuit

class CircuitCircle(Circuit):
    def __init__(self, config):
        super(CircuitCircle, self).__init__(config['circuit_circle'])
        surface_dim = (2*config['width']//3, config['height'])
        self.center = [config['width']//3 + surface_dim[0] // 2, surface_dim[1] // 2]
        self.center_draw = [surface_dim[0] // 2, surface_dim[1] // 2]
        self.inner_circle = config['circuit_circle']['inner_circle']
        self.outter_circle = config['circuit_circle']['outter_circle']
        self.surface = pygame.Surface(surface_dim)
        self.start = [self.center[0] - (self.outter_circle + self.inner_circle) // 2,
                                    self.center[1]]
        self.num_of_sectors = 36
    
    def draw(self):
        """Returns the pygame.Surface with the track drawed"""
        self.surface.set_colorkey((0, 255, 0))
        self.surface.fill((0,255,0))
        pygame.draw.circle(self.surface, self.color_wall, self.center_draw,
                            self.outter_circle)    
        pygame.draw.circle(self.surface, self.color_slow_area, self.center_draw,
                            self.outter_circle - self.wall)
        pygame.draw.circle(self.surface, self.color_background, self.center_draw,
                            self.outter_circle - self.slow_area - self.wall)    
        pygame.draw.circle(self.surface, self.color_slow_area, self.center_draw,
                            self.inner_circle + self.slow_area)    
        pygame.draw.circle(self.surface, self.color_wall, self.center_draw,
                            self.inner_circle)    
        pygame.draw.circle(self.surface, self.color_background, self.center_draw,
                            self.inner_circle - self.wall)    
        return self.surface

    def collision(self, shape):
        """Returns the type of collision of the shapely shape and the circuit.
        Can be NONE, SLOW_AREA or WALL."""
        if isinstance(shape, (Polygon, LineString)):
            points = self.get_points_shape(shape)
        else:
            points = shape
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