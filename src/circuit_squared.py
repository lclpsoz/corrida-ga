import pygame
from car import car
from view import view
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import numpy as np

class circuitSquared():
    def __init__(self, wall_color = (0, 0, 0)):
        offset = np.asarray([400, 100])
        self.surface = pygame.Surface((round(1200), round(600)))
        self.surface.set_colorkey((0, 255, 0))
        self.surface.fill((0, 255, 0))
        self.outside_walls = [  np.asarray([[0, 0],[400, 0],[400, 2],[0, 2]]) + offset,
                                np.asarray([[0, 0],[0, 400],[2, 400],[2, 0]]) + offset,
                                np.asarray([[0, 400],[400, 400],[400, 402],[0, 402]]) + offset,
                                np.asarray([[400, 400],[400, 0],[402, 0],[402, 400]]) + offset]
        self.pols_walls = [Polygon(wall) for wall in self.outside_walls]
        # self.pols_slow_areas = []
        
        [pygame.draw.polygon(self.surface, wall_color, wall) for wall in self.outside_walls]

    def collision(self, shape):
        """Returns the type of collision of the shapely shape and the circuit.
        Can be 0, 1, 2, that means none, outside of the path and wall,
        respectively."""
        if any([pol.intersects(shape) for pol in self.pols_walls]):
            return 1
        # elif any([pol.intersects(shape) for pol in self.pols_slow_areas]):
        #   return 2
        return 0

    def collision_car(self, player):
        """Returns the type of collision of the car and the circuit. Can be
        Can be 0, 1, 2, that means none, outside of the path and wall,
        respectively."""
        return self.collision(Polygon(player.get_points()))

    def get_surface(self):
        """Returns surface of the circuit."""
        return self.surface
        