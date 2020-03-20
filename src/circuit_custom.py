import pygame
import math
from circuit import Circuit
import time
import collisions_wrapper
import ctypes
from shapely.geometry import LineString
from shapely.geometry.polygon import Polygon
from shapely.geometry.point import Point
import numpy as np

class CircuitCustom(Circuit):
    def __init__(self, config, circuit_name):
        self.config = config
        circuit_name = 'circuit_' + circuit_name
        super(CircuitCustom, self).__init__(config[circuit_name])
        surface_dim = (2*config['width']//3, config['height'])
        self.surface = pygame.Surface(surface_dim)
        
        self.track_points = [config[circuit_name]['outter'], config[circuit_name]['inner']]
        a, b = self.track_points
        self.sectors = [[a[i], b[i]] for i in range(len(a))]
        self.num_of_sectors = len(self.sectors) - 1
        self.start = [
            (self.sectors[self.num_of_sectors - 1][0][0] +
                self.sectors[self.num_of_sectors - 1][1][0]) // 2 +
                config['width']//3,
            (self.sectors[self.num_of_sectors - 1][0][1] +
                self.sectors[self.num_of_sectors - 1][1][1]) // 2
            ]
        
        self.poly_sector = []
        last1, last2 = self.sectors[0]
        for i in range(1, self.num_of_sectors + 1):
            a, b = self.sectors[i]
            self.poly_sector.append(Polygon([last1, a, b, last2]))
            last1 = a
            last2 = b

        self.outter = Polygon(self.track_points[0])
        self.inner = Polygon(self.track_points[1])

    def draw(self):
        """Returns the pygame.Surface with the track drawed"""
        self.surface.set_colorkey((0, 255, 0))
        self.surface.fill((0,255,0))

        for container in range(0, 2):
            if len(self.track_points[container]) > 0:
                last = self.track_points[container][len(self.track_points[container]) - 1]
                for x, y in self.track_points[container]:
                    pygame.draw.line(self.surface, self.color_wall, [x, y], last, self.wall)
                    last = [x, y]

        return self.surface


    def sign(self, val):
        if val < 0:
            return -1
        elif val == 0:
            return 0
        else:
            return 1

    def collision(self, shape):
        """Returns the type of collision of the shapely shape and the circuit.
        Can be NONE, SLOW_AREA or WALL. Also accept list of points"""
        if isinstance(shape, (Polygon, LineString)):
            points = self.get_points_shape(shape)
        else:
            points = shape
        c = Circuit.COLLISION_NONE

        for x, y in points:
            x -= self.config['width']//3

            if self.inner.contains(Point(x,y)) or not self.outter.contains(Point(x,y)):
                c = Circuit.COLLISION_WALL            

        return c


    # def batch_collision_car(self, list_cars):
    #     """Returns a list of types of collisions, each position corresponding
    #     to each car in list_cars."""
    #     if collisions_wrapper.collisions:
    #         ret = []
    #         x = []
    #         y = []
    #         shapes_sizes = []
    #         for car in list_cars:
    #             pts = car.get_points()
    #             shapes_sizes.append(len(pts))
    #             for a, b in pts:
    #                 x.append(a)
    #                 y.append(b)
    #         cols_points = self.batch_collision_points(x, y)
    #         p_now = 0
    #         for shape_sz in shapes_sizes:
    #             maxi = -1
    #             for i in range(p_now, p_now + shape_sz):
    #                 maxi = max(maxi, cols_points[i])
    #             ret.append(maxi)
    #             p_now += shape_sz
    #         assert(len(ret) == len(list_cars))
    #         return ret
    #     else:
    #         return [self.collision_car(car) for car in list_cars]

    # def batch_collision(self, list_shapes : list):
    #     """Returns a list of types of collisions, each position corresponding
    #     to each shape in list_shapes."""
    #     if collisions_wrapper.collisions:
    #         ret = []
    #         x = []
    #         y = []
    #         shapes_sizes = []
    #         for shape in list_shapes:
    #             shapes_sizes.append(len(shape))
    #             for a, b in shape:
    #                 x.append(a)
    #                 y.append(b)
    #         cols_points = self.batch_collision_points(x, y)
    #         p_now = 0
    #         for shape_sz in shapes_sizes:
    #             maxi = -1
    #             for i in range(p_now, p_now + shape_sz):
    #                 maxi = max(maxi, cols_points[i])
    #             ret.append(maxi)
    #             p_now += shape_sz
    #         assert(len(ret) == len(list_shapes))
    #         return ret
    #     else:
    #         return [self.collision(shape) for shape in list_shapes]

    # def batch_collision_points(self, x, y):
    #     """Receives points as two lists and returns the type of collision for
    #     each."""
    #     n = len(x)
    #     x = (ctypes.c_float * n)(*x)
    #     y = (ctypes.c_float * n)(*y)
    #     outter_x = (ctypes.c_float * len(self.track_points[0]))(*[p[0] for p in self.track_points[0]])
    #     outter_y = (ctypes.c_float * len(self.track_points[0]))(*[p[1] for p in self.track_points[0]])
    #     inner_x = (ctypes.c_float * len(self.track_points[1]))(*[p[0] for p in self.track_points[1]])
    #     inner_y = (ctypes.c_float * len(self.track_points[1]))(*[p[1] for p in self.track_points[1]])
    #     sector = (ctypes.c_int * n)(*[self.cur_sector([x[i], y[i]]) for i in range(n)])
    #     return collisions_wrapper.col_circuit_custom(x, y, sector, outter_x, outter_y, inner_x, inner_y,
    #                                                     self.wall, self.slow_area, n)

    def cur_sector(self, point):
        """Returns the sector of a point"""
        id = -1
        x, y = point
        x -= self.config['width']//3
        for i in range(0, self.num_of_sectors):
            if self.poly_sector[i].contains(Point(x, y)):
                id = i
        return id


    def update_car_sector(self, car_id, player):
        """Updates the sector of the car (maximum sector of all its points)"""
        now = -1
        for p in player.get_points():
            now = max(now, self.cur_sector(p))

        if ((self.car_current_sector[car_id] + 1) % self.num_of_sectors == now) and\
                (self.car_sectors[car_id][self.car_current_sector[car_id]] == 1):
            self.car_sectors[car_id][now] = 1

        self.car_current_sector[car_id] = now