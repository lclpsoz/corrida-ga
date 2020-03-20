import pygame
import numpy as np
from circuit_custom import CircuitCustom

class CircuitMaker(object):
    def __init__(self, config):
        surface_dim = (2*config['width']//3, config['height'])
        self.surface = pygame.Surface(surface_dim)
        self.track_points = [[],[]]
        self.config = config
    
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

        if len(self.track_points[0]) > 0:
            last = self.track_points[0][0]
            for x, y in self.track_points[0]:
                # Draw point
                pygame.draw.rect(self.surface, (0,0,0), (x, y, 5, 5))
                # Draw line segment between current point and last point
                pygame.draw.line(self.surface, (0,0,0), [x, y], last, 2)
                last = [x, y]

        if len(self.track_points[1]) > 0:
            last = self.track_points[1][0]
            i = 0
            for x, y in self.track_points[1]:
                # Draw point
                pygame.draw.rect(self.surface, (0,0,0), (x, y, 5, 5))
                # Draw line segment between current point and last point
                pygame.draw.line(self.surface, (0,0,0), [x, y], last, 2)
                # Draw sector line
                pygame.draw.line(self.surface, (255,0,0), [x,y], self.track_points[0][i])
                last = [x, y]
                i += 1

        return self.surface
            
    def get_circuit(self):
        if not 'circuit_custom' in self.config:
            self.config['circuit_custom'] = {}
        self.config['circuit_custom']['outter'] = self.track_points[0]
        self.config['circuit_custom']['inner'] = self.track_points[1]
        return CircuitCustom(self.config, 'custom')

    def print_points(self):
        print("outter: ", self.track_points[0])
        print("inner: ", self.track_points[1])