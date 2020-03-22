import pygame
import numpy as np

from circuit.circuit import Circuit

class CircuitMaker(object):
    def __init__(self, config):
        self.surface_dim = (2*config['width']//3, config['height'])
        self.surface = pygame.Surface(self.surface_dim)
        self.track_points = [[],[]]
        self.config = config
        self.base_image_surface = pygame.Surface(self.surface_dim)
        self.base_image_path = self.config['circuit_custom']['base_image_path']


    def draw_base_image(self):
        if self.base_image_path != "":
            self.base_image_surface = pygame.image.load(self.base_image_path).convert()
            pygame.transform.scale(self.base_image_surface, self.surface_dim)
            self.base_image_surface.set_alpha(50)
        else:
            self.base_image_surface.set_colorkey((0, 255, 0))
            self.base_image_surface.fill((0,255,0))
        return self.base_image_surface
    
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
        return Circuit(self.config, 'custom')

    def print_points(self):
        print("outter: ", self.track_points[0])
        print("inner: ", self.track_points[1])