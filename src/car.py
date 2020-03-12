import pygame
import time
import math
import numpy as np
from shapely import affinity
from shapely.geometry import LineString
from shapely.geometry.polygon import Polygon
from circuit import Circuit

class Car():
    def __init__(self, config):
        """Receives information about the car. start_angle is relative to East and is
        anti-clockwise."""
        self.config = config
        if config['number_of_visions'] < 3:
            exit(0)
        self.frame_time = 1/config['fps']
        self.car_width = config['car_width']
        self.car_height = config['car_height']

        self.set_default_settings()

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
        self.direction = np.asarray([1, 0])
        # Delta per iteration in amount of pixels
        self.delta_pixels = 0  
        # Acceleration in amount of pixels per iteration
        self.acc_pixels = 0.1

        surface_side = 1.4*max(max(config['car_width'], config['car_height']), 2*config['vision_length'])
        self.center = [round(surface_side/2), round(surface_side/2)]
        self.x -= self.center[0]
        self.y -= self.center[1]

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
        self.vision_angles = np.linspace(-90, 90, config['number_of_visions'])
        self.vision = [False for x in range(config['vision_length'])] # False, no collision
        self.car_vision_colors = config['car_vision_colors']
        car_seg_vision_base = [self.center[0], self.center[1] + config['vision_length']]
        for angle_vision in self.vision_angles:
            self.car_seg_vision.append(self.rotate_point_degree(self.center, car_seg_vision_base, -angle_vision))

        # -90 makes car orientation to East, update_car_angle is clockwise,
        # -start_angle because start_angle is anti-clockwise.
        self.update_car_angle(-90 + -config['start_angle'])
        self.direction = self.rotate_point_degree((0, 0), self.direction, -config['start_angle'])

        # self.car_structure_orientations = self.generate_orientations(self.car_structure, 360)
        # self.car_front_orientations = self.generate_orientations(self.car_front, 360)

        self.surface = pygame.Surface((round(surface_side), round(surface_side)))
        self.surface.set_colorkey((0, 255, 0))
        self.surface.fill((0, 255, 0))

    def reset(self):
        """Resets car to default configurations."""
        self.set_default_settings()

    # def generate_orientations(self, base, amount):
    #     pass

    def handle_keys(self):
        """Do action based on pressed key."""
        key = pygame.key.get_pressed()
        turn_angle_intensity = max(2.25, (16 - self.delta_pixels)/3)
        turn_angle = 0
        if key[pygame.K_LEFT]:
            if(self.delta_pixels > self.EPS):
                turn_angle += -turn_angle_intensity
                # self.delta_pixels *= 1-self.friction_turn_loss_percentage
        if key[pygame.K_RIGHT]:
            if(self.delta_pixels > self.EPS):
                turn_angle += turn_angle_intensity
                # self.delta_pixels *= 1-self.friction_turn_loss_percentage
        if key[pygame.K_UP]:
            self.delta_pixels += self.acc_pixels

        # Apply turn
        self.direction = self.rotate_point_degree((0, 0), self.direction, turn_angle)
        self.update_car_angle(turn_angle)

        # Breaking
        if key[pygame.K_DOWN]:
            self.delta_pixels = max(0, self.delta_pixels-1.5*self.acc_pixels)

        # Apply movement
        self.x += self.direction[0]*self.delta_pixels
        self.y += self.direction[1]*self.delta_pixels

        # Apply friction
        speed = self.get_speed()
        if not key[pygame.K_UP] and speed > 0 and speed < 5:
            self.delta_pixels = max(0, self.delta_pixels -\
                0.2*self.friction_multiplier*self.friction_movement)
        else:
            self.delta_pixels *= 1 - self.friction_multiplier * self.friction_movement

    def update_car_angle(self, angle):
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
        return np.asarray([qx, qy])

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

    def update_vision(self, track):
        """Updates list vision, checking for collision with each vision
        segment."""
        for i in range(len(self.car_seg_vision)):
            line = LineString([np.array(self.center) + np.array([self.x, self.y]),
                                np.array(self.car_seg_vision[i]) + np.array([self.x, self.y])])
            self.vision[i] = track.collision(line) == Circuit.COLLISION_WALL

    def draw(self):
        """Updates surface based on changes in the car shape."""
        self.surface.fill((0, 255, 0))
        pygame.draw.polygon(self.surface, self.car_color, self.car_structure)
        pygame.draw.polygon(self.surface, self.front_color, self.car_front)
        for i in range(len(self.car_seg_vision)):
            pygame.draw.line(self.surface, self.car_vision_colors[self.vision[i]],
                self.center, self.car_seg_vision[i])
        return self.surface

    def set_friction_multiplier(self, friction_multiplier):
        self.friction_multiplier = friction_multiplier

    def get_pos_surface(self):
        """Return position of the surface in the screen."""
        return [round(self.x), round(self.y)]

    def get_pos(self):
        """Return position of the center of the car as a np array."""
        # return np.array([round(self.x), round(self.y)], dtype=np.int) + np.array(self.center, dtype=np.int)
        return np.array(self.get_pos_surface()) + np.array(self.center)

    def get_points(self):
        """Returns position of each point of the car as a list of np array."""
        ret = []
        for pt in self.car_structure:
            ret.append(np.array([self.x, self.y]) + np.array(pt))

        return ret

    def get_speed_squared(self):
        """Returns the speed of the car in meters per second squared."""
        return self.delta_pixels/self.frame_time
    
    def get_speed(self):
        """Returns the speed of the car in meters per second."""
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