import pygame
import time
import math
import numpy as np
from shapely import affinity
from shapely.geometry import LineString
from shapely.geometry.polygon import Polygon
from copy import deepcopy

from circuit.circuit import Circuit

class Car():
    MOVE_ACC = 0
    MOVE_TURN = 1
    def __init__(self, config, show_vision = False):
        """Receives information about the car. start_angle is relative to East and is
        anti-clockwise."""
        self.config = config
        if config['number_of_visions'] < 3:
            print("number_of_visions < 3.")
            exit(0)
        self.amount_graphics = config['amount_graphics']
        if 360%self.amount_graphics:
            print("360%amount_graphics != 0")
            exit(0)
        self.car_width = config['car_width']
        self.car_height = config['car_height']
        self.vision_length = config['vision_length']

        self.set_default_settings()
        self.generate_car_graphics()
        self.update_car_angle()

        self.show_vision = show_vision
        
        self.mov_norm = 2

    def set_default_settings(self):
        config = self.config
        self.x = config['x']
        self.y = config['y']
        self.car_color = config['car_color']
        self.front_color = config['front_color']

        self.EPS = 1e-6

        # The car is 1m x 2m, so, the amount of pixels in it car_width is a meter.
        self.pixels_per_meter = config['car_width']

        self.friction_movement = 0.005
        self.friction_multiplier = 1
        # self.friction_turn_loss_percentage = 0.000
        # Direction is stored as a unit vector
        self.direction = [1, 0]
        # Delta per iteration in amount of pixels
        self.delta_pixels = 0  
        # Acceleration in amount of pixels per iteration
        self.acc_pixels = 0.1

        self.surface_side = 1.4*max(max(config['car_width'], config['car_height']), 2*self.vision_length)
        self.center = [round(self.surface_side/2), round(self.surface_side/2)]
        self.x -= self.center[0]
        self.y -= self.center[1]

        # -start_angle because start_angle is anti-clockwise.
        self.direction = self.rotate_point_degree((0, 0), self.direction, -config['start_angle'])

        self.movement = [0, 0] # ACC and TURN

    def reset(self):
        """Resets car to default configurations."""
        self.set_default_settings()
        self.update_car_angle()

    def generate_car_graphics(self):
        self.car_structure = [  (self.center[0] - self.car_width/2, self.center[1] - self.car_height/2),
                                (self.center[0] + self.car_width/2, self.center[1] - self.car_height/2),
                                (self.center[0] + self.car_width/2, self.center[1] + self.car_height/2),
                                (self.center[0] - self.car_width/2, self.center[1] + self.car_height/2) ]
        self.car_front = [      (self.center[0] - self.car_width/2, self.center[1] + self.car_height/4),
                                (self.center[0] + self.car_width/2, self.center[1] + self.car_height/4),
                                (self.center[0] + self.car_width/2, self.center[1] + self.car_height/2),
                                (self.center[0] - self.car_width/2, self.center[1] + self.car_height/2) ]

        # Car Vision
        self.car_seg_vision = []
        self.vision_angles = np.linspace(-90, 90, self.config['number_of_visions'])
        self.vision = [1.0 for x in range(self.config['number_of_visions'])] # False, no collision
        self.car_vision_colors = self.config['car_vision_colors']
        car_seg_vision_base = [self.center[0], self.center[1] + self.vision_length]
        for angle_vision in self.vision_angles:
            self.car_seg_vision.append(self.rotate_point_degree(self.center, car_seg_vision_base, -angle_vision))

        # -90 makes car orientation to East, update_car_angle_exact is clockwise
        self.update_car_angle_exact(-90)

        # Start PyGame surface for the car
        if self.config["graphics"]:
            self.surface = pygame.Surface((round(self.surface_side), round(self.surface_side)), pygame.SRCALPHA)
        self.ori_car_structure = []
        self.ori_car_front = []
        self.ori_car_seg_vision = []
        self.generate_orientations(self.amount_graphics)

    def generate_orientations(self, amount):
        """Generate orientations based on the amount of samples from 360 degress."""
        for x in range(0, 360 + 1, 360//amount):
            self.ori_car_structure.append(deepcopy(self.car_structure))
            self.ori_car_front.append(deepcopy(self.car_front))
            self.ori_car_seg_vision.append(deepcopy(self.car_seg_vision))
            self.update_car_angle_exact(-360//amount)

    def apply_turn(self):
        # Apply turn to the car based on list movement
        turn_angle_intensity = max(2.25, (16 - self.delta_pixels)/3)
        turn_angle = 0
        intensity = min(1, self.movement[self.MOVE_TURN]/self.mov_norm)
        # When the movement is positive, it must turn left, right otherwise
        if self.movement[self.MOVE_TURN] > 0:
            if(self.delta_pixels > self.EPS):
                turn_angle += -turn_angle_intensity*intensity
        else:
            if(self.delta_pixels > self.EPS):
                turn_angle += turn_angle_intensity*-intensity

        self.direction = self.rotate_point_degree((0, 0), self.direction, turn_angle)
        self.update_car_angle()

    def apply_movement(self):
        # Apply movement to the car based on list movement
        self.apply_turn()
        
        intensity = min(1, self.movement[self.MOVE_ACC]/self.mov_norm)
        # If movement in MOVE_ACC is positive, it will accelerate. The
        # car will break otherwise.
        if self.movement[self.MOVE_ACC] > 0:
            self.delta_pixels += self.acc_pixels*intensity

        # Breaking
        else:
            brk = 1.5*self.acc_pixels*-intensity
            self.delta_pixels = max(0, self.delta_pixels-brk)

        # Apply acceleration
        self.x += self.direction[0]*self.delta_pixels
        self.y += self.direction[1]*self.delta_pixels

        # Apply friction
        speed = self.get_speed()
        self.delta_pixels *= 1 - self.friction_multiplier * self.friction_movement


    def handle_keys(self):
        """Updates movement based on pressed key(s)."""
        key = pygame.key.get_pressed()
        self.movement = [0, 0, 0, 0]
        if key[pygame.K_UP]:
            self.movement[0] = self.mov_norm
        elif key[pygame.K_DOWN]:
            self.movement[0] = -self.mov_norm
        if key[pygame.K_LEFT]:
            self.movement[1] = self.mov_norm
        elif key[pygame.K_RIGHT]:
            self.movement[1] = -self.mov_norm
        
        return self.movement

    def update_car_angle_exact(self, angle):
        """Updates car graphics by the angle parameter in degrees. Rotates
        clockwise"""
        # Car structure
        points = self.car_structure
        pol = affinity.rotate(Polygon(points), angle)
        points_sep = pol.exterior.coords.xy
        for i in range(len(points)):
            points[i] = (points_sep[0][i], points_sep[1][i])

        # Car front
        points = self.car_front
        pol = affinity.rotate(Polygon(points), angle, self.center)
        points_sep = pol.exterior.coords.xy
        for i in range(len(points)):
            points[i] = (points_sep[0][i], points_sep[1][i])

        # Vision
        for i in range(len(self.car_seg_vision)):
            self.car_seg_vision[i] = self.rotate_point_degree(self.center, self.car_seg_vision[i], angle)

    def update_car_angle(self):
        """Updates car graphics based on the angle of the velocity vector. Rotates
        clockwise with predetermined precision."""
        idx = int(round(self.get_angle_degrees()/(360/self.amount_graphics)))

        self.car_structure = self.ori_car_structure[idx]
        self.car_front = self.ori_car_front[idx]
        self.car_seg_vision = self.ori_car_seg_vision[idx]

    def rotate_point_degree(self, origin, point, angle):
        """
        Rotate a point clockwise by a given angle around a given origin.

        The angle should be given in degrees.
        """
        return self.rotate_point(origin, point, (angle*math.pi)/180)

    def rotate_point(self, origin, point, angle):
        """
        Rotate a point clockwise by a given angle around a given origin.

        The angle should be given in radians.
        """
        ox, oy = origin
        px, py = point

        qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
        qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
        return [qx, qy]

    def vector_magnitude_sum(self, vector, scalar):
        """Sum scalar value to vector magnitude."""
        vector = np.asarray(vector)
        x, y = vector
        vector_magnitude = math.sqrt(x**2 + y**2)
        if vector_magnitude > 0:
            vector_unit = vector/vector_magnitude
        else:
            vector_unit = [1, 0]
        return vector + (vector_unit*scalar)

    def draw(self):
        """Updates surface based on changes in the car shape."""
        self.surface = pygame.Surface((round(self.surface_side), round(self.surface_side)), pygame.SRCALPHA)
        pygame.draw.polygon(self.surface, self.car_color, self.car_structure)
        pygame.draw.polygon(self.surface, self.front_color, self.car_front)
        if self.show_vision:
            for i in range(len(self.car_seg_vision)):
                vector = [self.car_seg_vision[i][0] - self.center[0],
                            self.car_seg_vision[i][1] - self.center[1]]
                delta = -(1-self.vision[i])*self.vision_length
                if delta > 0:
                    delta = 0
                vector = self.vector_magnitude_sum(vector, delta)
                vector[0] += self.center[0]
                vector[1] += self.center[1]
                pygame.draw.line(
                    self.surface, (0, 254, 0),
                    self.center,
                    vector)
        return self.surface

    def set_friction_multiplier(self, friction_multiplier):
        self.friction_multiplier = friction_multiplier

    def get_pos_surface(self):
        """Return position of the surface in the screen."""
        return [round(self.x), round(self.y)]

    def get_pos(self):
        """Return position of the center of the car as a list."""
        cx, cy = self.center
        x, y = self.get_pos_surface()
        return [cx + x, cy + y]

    def get_points(self):
        """Returns position of each point of the car as a list of lists."""
        ret = []
        for x, y in self.car_structure:
            ret.append([self.x + x, self.y + y])

        return ret

    def get_points_vision(self):
        """Returns list with vision segments as lists."""
        list_vision = []
        cx, cy = self.center
        for x, y in self.car_seg_vision:
            list_vision.append([[self.x + cx, self.y + cy],
                                [self.x + x, self.y + y]])
        return list_vision

    def get_speed_squared(self):
        """Returns the speed of the car in meters per second squared. Approximated
        considering 120 FPS."""
        return 120 * self.delta_pixels
    
    def get_speed(self):
        """Returns the speed of the car in meters per second. Approximated
        considering 120 FPS."""
        return math.sqrt(self.get_speed_squared())

    def get_angle(self):
        """Returns the angle of the speed vector of the car in radians."""
        angle = math.atan2(self.direction[0], self.direction[1])
        if(angle < 0):
            angle = 2*math.pi+angle
        angle = angle - math.pi/2
        if(angle < 0):
            angle += 2*math.pi
        return angle

    def get_angle_degrees(self):
        """Returns the angle of the speed vector of the car in degress."""
        return self.get_angle()*180/math.pi 

    @staticmethod
    def get_controls():
        """Returns multiple strings with manual controls information."""
        return ["Arrow up: Accelerate the car forward.",
                "Arrow down: Breaks.",
                "Arrows to sides: Change the car direction."]