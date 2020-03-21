import pygame
import math
import time
import ctypes
from shapely.geometry import LineString
from shapely.geometry.polygon import Polygon
from shapely.geometry.point import Point

from circuit.circuit import Circuit
import collisions_wrapper

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

        self.sector_points = []
        for i in range(self.num_of_sectors):
            a, b = self.sectors[i]
            c, d = self.sectors[i + 1]
            self.sector_points.append([a, c, d, b])

        self.point_max_sector = []

    def add_car(self, player, frame_now):
        """Adds a car in the circuit."""
        id = len(self.car_sectors)
        self.car_sectors.append([0 for i in range(self.num_of_sectors)])
        self.car_sectors[id][0] = 1
        self.car_current_sector.append(0)
        self.car_start_time.append(time.time())
        self.car_start_frame.append(frame_now)
        self.point_max_sector.append(self.num_of_sectors - 1)

        return id

    def reset(self, car_id, frame_now):
        """Reset car with car_id."""
        self.car_sectors[car_id] = [0 for i in range(self.num_of_sectors)]
        self.car_sectors[car_id][0] = 1
        self.car_current_sector[car_id] = 0
        self.car_start_time[car_id] = time.time()
        self.car_start_frame[car_id] = frame_now
        self.point_max_sector[car_id] = self.num_of_sectors - 1

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

        # last = self.track_points[1][0]
        # i = 0
        # for x, y in self.track_points[1]:
        #     # Draw sector line
        #     pygame.draw.line(self.surface, (255,0,0), [x,y], self.track_points[0][i])
        #     last = [x, y]
        #     i += 1        
        return self.surface

    def collision(self, shape):
        """Returns the type of collision of the shapely shape and the circuit.
        Can be NONE, SLOW_AREA or WALL. Also accept list of points"""
        if isinstance(shape, (Polygon, LineString)):
            points = self.get_points_shape(shape)
        else:
            points = shape
        c = Circuit.COLLISION_NONE
        for x, y in points:
            sector_id = self.cur_sector([x,y])
            if sector_id == -1:
                c = Circuit.COLLISION_WALL

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
                    x.append(a - self.config['width']//3)
                    y.append(-b)
            batch_ret = self.batch_collision_points(x, y)
            p_now = 0
            for shape_sz in shapes_sizes:
                maxi_sec = -1
                maxi_col = -1
                for i in range(p_now, p_now + shape_sz):
                    maxi_sec = max(maxi_sec, batch_ret[0][i])
                    maxi_col = max(maxi_col, batch_ret[1][i])
                self.point_max_sector[len(ret)] = maxi_sec
                ret.append(maxi_col)
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
                    x.append(a - self.config['width']//3)
                    y.append(-b)
            cols_points = self.batch_collision_points(x, y)
            p_now = 0
            for shape_sz in shapes_sizes:
                maxi = -1
                for i in range(p_now, p_now + shape_sz):
                    maxi = max(maxi, cols_points[1][i])
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
        outter_x = (ctypes.c_float * len(self.track_points[0]))(*[p[0] for p in self.track_points[0]])
        outter_y = (ctypes.c_float * len(self.track_points[0]))(*[p[1] for p in self.track_points[0]])
        inner_x = (ctypes.c_float * len(self.track_points[1]))(*[p[0] for p in self.track_points[1]])
        inner_y = (ctypes.c_float * len(self.track_points[1]))(*[p[1] for p in self.track_points[1]])
        return collisions_wrapper.col_circuit_custom(x, y, self.num_of_sectors, outter_x, outter_y, inner_x, inner_y,
                                                        self.wall, self.slow_area, n)

    def cross(self, x1, y1, x2, y2):
        return (x1 * y2) - (x2 * y1)
    
    def sign(self, x):
        return (-1 if x < 0 else 1 if x > 0 else 0)

    def contains(self, sector_id, x, y):
        outter_ax, outter_ay = self.sector_points[sector_id][0].copy()
        outter_bx, outter_by = self.sector_points[sector_id][1].copy()
        inner_bx, inner_by = self.sector_points[sector_id][2].copy()
        inner_ax, inner_ay = self.sector_points[sector_id][3].copy()
        outter_ay = -outter_ay
        outter_by = -outter_by
        inner_ay = -inner_ay
        inner_by = -inner_by


        c_sector1 = self.cross(outter_ax - inner_ax, outter_ay - inner_ay,
                    x - inner_ax, y - inner_ay)
        c_sector2 = self.cross(outter_bx - inner_bx, outter_by - inner_by,
                    x - inner_bx, y - inner_by)

        c_sector1 = self.sign(c_sector1)
        c_sector2 = self.sign(c_sector2)
        
        if c_sector1 == c_sector2:
            return False

        c_outter = self.cross(outter_bx - outter_ax, outter_by - outter_ay,
                    x - outter_ax, y - outter_ay)
        c_inner = self.cross(inner_bx - inner_ax, inner_by - inner_ay,
                    x - inner_ax, y - inner_ay)

        c_outter = self.sign(c_outter)
        c_inner = self.sign(c_inner)

        if c_outter == c_inner:
            return False
        
        return True

    def cur_sector(self, point):
        """Returns the sector of a point"""
        id = -1
        x, y = point
        for i in range(0, self.num_of_sectors):
            if self.contains(i, x - self.config['width']//3, -y):
                id = i
        return id

    def update_car_sector(self, car_id, player):
        """Updates the sector of the car (maximum sector of all its points)"""
        now = -1
        if collisions_wrapper.collisions:
            now = self.point_max_sector[car_id]
        else:
            for p in player.get_points():
                now = max(now, self.cur_sector(p))
        
        if ((self.car_current_sector[car_id] + 1) % self.num_of_sectors == now) and\
                (self.car_sectors[car_id][self.car_current_sector[car_id]] == 1):
            self.car_sectors[car_id][now] = 1

        self.car_current_sector[car_id] = now