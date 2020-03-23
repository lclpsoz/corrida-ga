import pygame
import math
import time
import ctypes
from copy import deepcopy
from shapely.geometry.polygon import Polygon
from shapely.geometry import LineString

import collisions_wrapper

class Circuit(object):
    COLLISION_NONE = 0
    COLLISION_WALL = 1

    def __init__(self, config, circuit_name):
        circuit_name = 'circuit_' + circuit_name
        self.config = config
        self.wall = config[circuit_name]['wall']
        self.start_angle = config[circuit_name]['start_angle']
        
        self.color_background = (255,255,255)
        self.color_wall = (0,0,0)

        self.car_start_time = []
        self.car_sectors = []
        self.car_current_sector = []
        self.car_start_frame = []

        self.x_shift = self.config['width']//3
        surface_dim = (2*config['width']//3, config['height'])
        if self.config["graphics"]:
            self.surface = pygame.Surface(surface_dim)
        
        self.track_points = [config[circuit_name]['outter'], config[circuit_name]['inner']]
        a, b = self.track_points
        self.sectors = deepcopy([[a[i], b[i]] for i in range(len(a))])
        self.num_of_sectors = len(self.sectors)
        self.start = [
            (self.sectors[0][0][0] +
                self.sectors[0][1][0]) // 2 +
                config['width']//3,
            (self.sectors[0][0][1] +
                self.sectors[0][1][1]) // 2
            ]
        for sector_line in self.sectors:
            sector_line[0][0] += self.x_shift
            sector_line[1][0] += self.x_shift

        self.point_max_sector = []

    def collision(self, shape):
        """Returns the type of collision of the shapely shape and the circuit.
        Can be NONE or WALL. Also accept list of points"""
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

    def get_walls_list(self):
        """Returns list of floats, each 4 positions representing a segment
        of the walls (inner and outter)."""
        walls = []
        for container in range(0, 2):
            if len(self.track_points[container]) > 0:
                last = self.track_points[container][0]
                for x, y in self.track_points[container][1:]:
                    walls.extend([last[0]+self.x_shift, last[1], x+self.x_shift, y])
                    last = [x, y]
        return walls

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

    def finished(self, car_id):
        """True if the car finished the circuit, False otherwise."""
        return sum(self.car_sectors[car_id]) == self.num_of_sectors

    def collision_car(self, car):
        """Returns the type of collision of the car and the circuit. Can be
        NONE or WALL."""
        return self.collision(Polygon(car.get_points()))

    def batch_collision_car(self, list_cars):
        """Returns a list of types of collisions, each position corresponding
        to each car in list_cars."""
        if collisions_wrapper.collisions:
            ret = []
            segs = []
            for car in list_cars:
                pts = car.get_points()
                last_x, last_y = pts[-1]
                for x, y in pts:
                    segs.extend([last_x, last_y, x, y])
                    last_x, last_y = x, y
            batch_ret = self.batch_collision_segs(segs, self.get_walls_list())
            for i in range(0, 4*len(list_cars), 4):
                now = Circuit.COLLISION_NONE
                for j in range(i, i+4):
                    if batch_ret[j]:
                        now = Circuit.COLLISION_WALL
                        break
                ret.append(now)

            assert(len(ret) == len(list_cars))
            # Free memory
            collisions_wrapper.freeme(batch_ret)
            return ret
        else:
            return [self.collision_car(car) for car in list_cars]

    def batch_collision(self, segs_input : list):
        """Returns a list of types of collisions, each position corresponding
        to the collision with the walls for each segment.
        segs is expected to be a list of elements in the format: [[x1, y1], [x2, y2]]"""
        if collisions_wrapper.collisions:
            ret = []
            segs_list = []
            for seg in segs_input:
                segs_list.extend([seg[0][0], seg[0][1], seg[1][0], seg[1][1]])
            batch_ret = self.batch_collision_segs(segs_list, self.get_walls_list())
            for i in range(len(segs_input)):
                if batch_ret[i]:
                    ret.append(Circuit.COLLISION_WALL)
                else:
                    ret.append(Circuit.COLLISION_NONE)

            assert(len(ret) == len(segs_input))
            # Free memory
            collisions_wrapper.freeme(batch_ret)
            return ret
        else:
            return [self.collision(shape) for shape in segs_input]

    def batch_collision_segs(self, segs_1, segs_2):
        """Receives two lists of segments and compute which of the first
        collide with any of the second."""
        n_segs_1 = len(segs_1)
        n_segs_2 = len(segs_2)
        segs_1 = (ctypes.c_float * n_segs_1)(*segs_1)
        segs_2 = (ctypes.c_float * n_segs_2)(*segs_2)
        n_segs_1//=4
        n_segs_2//=4
        return collisions_wrapper.col_circuit(segs_1, n_segs_1, segs_2, n_segs_2)

    def batch_collision_dist(self, segs_input : list):
        """Returns a list of distance to the first collision, each position corresponding
        to the collision with the walls for each segment.
        segs is expected to be a list of elements in the format: [[x1, y1], [x2, y2]]"""
        if collisions_wrapper.collisions:
            ret = []
            segs_list = []
            for seg in segs_input:
                segs_list.extend([seg[0][0], seg[0][1], seg[1][0], seg[1][1]])
            batch_ret = self.batch_collision_dist_segs(segs_list, self.get_walls_list())
            for i in range(len(segs_input)):
                ret.append(batch_ret[i])

            # Free memory
            collisions_wrapper.freeme(batch_ret)
            return ret
        else:
            return [self.collision(shape) for shape in segs_input]

    def batch_collision_dist_segs(self, segs_1, segs_2):
        """Receives two lists of segments. Returns the distance between
        each segment in segs_1 to the first segment collision in segs_2."""
        n_segs_1 = len(segs_1)
        n_segs_2 = len(segs_2)
        segs_1 = (ctypes.c_float * n_segs_1)(*segs_1)
        segs_2 = (ctypes.c_float * n_segs_2)(*segs_2)
        n_segs_1 //= 4
        n_segs_2 //= 4
        return collisions_wrapper.col_dist_circuit(segs_1, n_segs_1, segs_2, n_segs_2)

    def update_car_sector(self, car_id, car):
        """Updates the sector of the car."""
        now = self.car_current_sector[car_id]
        segs = []
        pts = car.get_points()
        last_x, last_y = pts[-1]
        for x, y in pts:
            segs.append([[last_x, last_y], [x, y]])
            last_x, last_y = x, y
        nxt_sector = True
        while nxt_sector and now < self.num_of_sectors:
            nxt_sector = False
            for seg in segs:
                if LineString(self.sectors[now]).intersects(LineString(seg)):
                    nxt_sector = True
                    break
            if nxt_sector:
                self.car_sectors[car_id][now] = 1
                now += 1

        self.car_current_sector[car_id] = now

    def get_points_shape(self, shape):
        """Receives any shapely shape and returns it points in a array"""
        if isinstance(shape, Polygon):
            shape = shape.exterior
        xy = shape.coords.xy
        points = [(xy[0][i], xy[1][i]) for i in range(len(xy[0]))]
        return points

    def get_current_car_time(self, car_id):
        """Returns current time by car with car_id."""
        return time.time() - self.car_start_time[car_id]

    def get_car_num_frames(self, car_id, frame_now):
        """Returns number of frames since the car was added."""
        return frame_now - self.car_start_frame[car_id]

    def get_car_perc_sectors(self, car_id):
        """Returns percentage of sectors already traversed by car with car_id."""
        return sum(self.car_sectors[car_id])/self.num_of_sectors