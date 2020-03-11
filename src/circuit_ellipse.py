import pygame
import math
import numpy as np
from circuit import Circuit
import time

class CircuitEllipse(Circuit):
    def __init__(self, center, inner, outter, gray, wall, slow_multiplier, start_angle, width, height):
        self.center = np.asarray(center)
        self.inner = inner
        self.outter = outter
        self.gray = gray
        self.wall = wall
        self.color1 = (0,0,0)
        self.color2 = (255,255,255)
        self.color3 = (220,220,220)
        self.surface = pygame.Surface((width, height))
        self.start = np.asarray([center[0] - (self.outter[0] + self.inner[0]) // 2,
                                    center[1]])
        self.start_angle = start_angle
        self.sectors = []
        self.current_sector = []
        self.start_time = []
        self.slow_friction_multiplier = slow_multiplier
    
    def draw(self):
        """Returns the pygame.Surface with the track drawed"""
        self.surface.set_colorkey((0, 255, 0))
        self.surface.fill((0,255,0))
        pygame.draw.ellipse(self.surface, self.color1, 
                            (self.center[0] - self.outter[0], self.center[1] - self.outter[1],
                            2 * self.outter[0], 2 * self.outter[1]))    
        pygame.draw.ellipse(self.surface, self.color3,
                            (self.center[0] - self.outter[0] + self.wall, self.center[1] - self.outter[1] + self.wall, 
                            2 * (self.outter[0] - self.wall), 2 * (self.outter[1] - self.wall)))
        pygame.draw.ellipse(self.surface, self.color2,
                            (self.center[0] - self.outter[0] + self.gray + self.wall, self.center[1] - self.outter[1] + self.gray + self.wall, 
                            2 * (self.outter[0] - self.gray - self.wall), 2 * (self.outter[1] - self.gray - self.wall)))
        pygame.draw.ellipse(self.surface, self.color3,
                            (self.center[0] - self.inner[0] - self.gray, self.center[1] - self.inner[1] - self.gray,
                            2 * (self.inner[0] + self.gray), 2 * (self.inner[1] + self.gray)))
        pygame.draw.ellipse(self.surface, self.color1,
                            (self.center[0] - self.inner[0], self.center[1] - self.inner[1],
                            2 * self.inner[0], 2 * self.inner[1]))
        pygame.draw.ellipse(self.surface, self.color2,
                            (self.center[0] - self.inner[0] + self.wall, self.center[1] - self.inner[1] + self.wall,
                            2 * (self.inner[0] - self.wall), 2 * (self.inner[1] - self.wall)))
        return self.surface

    def reset(self, player_id):
        self.sectors[player_id] = [0 for i in range(36)]
        self.sectors[player_id][0] = 1
        self.current_sector[player_id] = 0
        self.start_time[player_id] = time.time()

    def collision(self, shape):
        """Returns the type of collision of the shapely shape and the circuit.
        Can be NONE, SLOW_AREA or WALL."""
        points = self.get_points_shape(shape)
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
            elif(d <= r2 + self.gray or
                d >= r1 - self.gray):
                c = Circuit.COLLISION_SLOW_AREA
        return c
        
    def add_car(self, player):
        """Adds a car in the circuit """
        id = len(self.sectors)
        self.sectors.append([0 for i in range(36)])
        self.sectors[id][0] = 1
        self.current_sector.append(0)
        self.start_time.append(time.time())
        return id

    def cur_sector(self, point):
        """Returns the sector of a point"""
        angle = math.atan2(-(point[1] - self.center[1]), point[0] - self.center[0])
        angle = math.degrees(angle)
        angle = 180 - angle
        if angle < 0:
            angle += 360
        return int(angle // 10)

    def update_sector(self, player_id, player):
        """Updates the sector of the car (maximum sector of all its points)"""
        now = -1
        for p in player.get_points():
            now = max(now, self.cur_sector(p))

        if ((self.current_sector[player_id] + 1) % 36 == now) and\
                (self.sectors[player_id][self.current_sector[player_id]] == 1):
            self.sectors[player_id][now] = 1

        self.current_sector[player_id] = now

    def finished(self, player_id):
        """True if the car finished the circuit, False otherwise"""
        for i in range(36):
            if self.sectors[player_id][i] == 0:
                return False
       
        return self.current_sector[player_id] == 0