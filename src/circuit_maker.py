import pygame
import numpy as np
from circuit_custom import CircuitCustom

class CircuitMaker(object):
    def __init__(self, config):
        self.surface = pygame.Surface((config['width'], config['height']))
        self.track_points = [[],[]]
    
    def add_point(self, x, y, container):
        self.track_points[container].append([x, y])

    def remove_last_point(self, container):
        self.track_points[container].pop()

    def finish(self, container):
        if len(self.track_points[container]) < 3:
            return 0
        x, y = self.track_points[container][0]
        self.add_point(x, y, container)
        return 1

    def draw(self):
        self.surface.set_colorkey((0, 255, 0))
        self.surface.fill((0,255,0))

        for container in range(0, 2):
            if len(self.track_points[container]) > 0:
                last = self.track_points[container][0]
                for x, y in self.track_points[container]:
                    # Draw point
                    pygame.draw.rect(self.surface, (0,0,0), (x, y, 5, 5))
                    # Draw line segment between current point and last point
                    pygame.draw.line(self.surface, (0,0,0), [x, y], last, 2)
                    last = [x, y]

        return self.surface
            
    def get_circuit(self):
        return CircuitCustom(self.track_points)