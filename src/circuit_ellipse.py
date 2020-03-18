import pygame
import math
from circuit import Circuit
import time
import collisions_wrapper
import ctypes
from shapely.geometry import LineString
from shapely.geometry.polygon import Polygon

class CircuitEllipse(Circuit):
    def __init__(self, config):
        super(CircuitEllipse, self).__init__(config['circuit_ellipse'])
        surface_dim = (2*config['width']//3, config['height'])
        self.center = [surface_dim[0] // 2, surface_dim[1] // 2]
        self.inner = config['circuit_ellipse']['inner']
        self.outter = config['circuit_ellipse']['outter']
        self.surface = pygame.Surface(surface_dim)
        self.start = [self.center[0] - (self.outter[0] + self.inner[0]) // 2,
                                    self.center[1]]
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
        Can be NONE, SLOW_AREA or WALL. Also accept list of points"""
        if isinstance(shape, (Polygon, LineString)):
            points = self.get_points_shape(shape)
        else:
            points = shape
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

    def batch_collision_car(self, list_cars):
        """Returns a list of types of collisions, each position corresponding
        to each car in list_cars."""
        if collisions_wrapper.collisions:
            ret = []
            x = []
            y = []
            shapes_sizes = []
            for car in list_cars:
                pts = car.get_points()
                shapes_sizes.append(len(pts))
                for a, b in pts:
                    x.append(a)
                    y.append(b)
            cols_points = self.batch_collision_points(x, y)
            p_now = 0
            for shape_sz in shapes_sizes:
                maxi = -1
                for i in range(p_now, p_now + shape_sz):
                    maxi = max(maxi, cols_points[i])
                ret.append(maxi)
                p_now += shape_sz
            assert(len(ret) == len(list_cars))
            return ret
        else:
            return [self.collision_car(car) for car in list_cars]

    def batch_collision(self, list_shapes : list):
        """Returns a list of types of collisions, each position corresponding
        to each shape in list_shapes."""
        if collisions_wrapper.collisions:
            ret = []
            x = []
            y = []
            shapes_sizes = []
            for shape in list_shapes:
                shapes_sizes.append(len(shape))
                for a, b in shape:
                    x.append(a)
                    y.append(b)
            cols_points = self.batch_collision_points(x, y)
            p_now = 0
            for shape_sz in shapes_sizes:
                maxi = -1
                for i in range(p_now, p_now + shape_sz):
                    maxi = max(maxi, cols_points[i])
                ret.append(maxi)
                p_now += shape_sz
            assert(len(ret) == len(list_shapes))
            return ret
        else:
            return [self.collision(shape) for shape in list_shapes]

    def batch_collision_points(self, x, y):
        """Receives points as two lists and returns the type of collision for
        each."""
        n = len(x)
        x = (ctypes.c_float * n)(*x)
        y = (ctypes.c_float * n)(*y)
        center = (ctypes.c_float * len(self.center))(*self.center)
        outter = (ctypes.c_float * len(self.outter))(*self.outter)
        inner = (ctypes.c_float * len(self.inner))(*self.inner)
        return collisions_wrapper.col_circuit_ellipse(x, y, center, outter, inner,
                                                        self.wall, self.slow_area, n)

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