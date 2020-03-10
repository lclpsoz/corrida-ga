import pygame
import math
import numpy as np
from circuit import Circuit
from shapely.geometry.polygon import Polygon

class CircuitCircle(Circuit):
    def __init__(self, center):
        self.center = np.asarray(center)
        self.inner_circle = 175
        self.outter_circle = 250
        self.gray = 15
        self.color1 = (0,0,0)
        self.color2 = (255,255,255)
        self.color3 = (220,220,220)
        self.surface = pygame.Surface((1200, 600))
        self.start = np.asarray([center[0] - (self.outter_circle + self.inner_circle) // 2,
                                    center[1]])
        self.sectors = []
        self.current_sector = []

    def draw(self):
        """Returns the pygame.Surface with the track drawed"""
        self.surface.set_colorkey((0, 255, 0))
        self.surface.fill((0,255,0))
        pygame.draw.circle(self.surface, self.color1, self.center,
                            self.outter_circle)    
        pygame.draw.circle(self.surface, self.color3, self.center,
                            self.outter_circle - 2)
        pygame.draw.circle(self.surface, self.color2, self.center,
                            self.outter_circle - self.gray - 2)    
        pygame.draw.circle(self.surface, self.color3, self.center,
                            self.inner_circle + self.gray)    
        pygame.draw.circle(self.surface, self.color1, self.center,
                            self.inner_circle)    
        pygame.draw.circle(self.surface, self.color2, self.center,
                            self.inner_circle - 2)    
        return self.surface

    def collision(self, shape):
        """Returns the type of collision of the shapely shape and the circuit.
        Can be NONE, SLOW_AREA or WALL."""
        points = self.get_points_shape(shape)
        for p in points:
            d = math.hypot(self.center[0] - p[0], self.center[1] - p[1])
            if d <= self.inner_circle or d >= self.outter_circle - 2:
                return Circuit.COLLISION_WALL
            if(d <= self.inner_circle + self.gray or
                d >= self.outter_circle - self.gray):
                return Circuit.COLLISION_SLOW_AREA
        return Circuit.COLLISION_NONE
        
        pass
        
    def add_player(self, player):
        """Adds a car in the circuit """
        id = len(self.sectors)
        self.sectors.append([0 for i in range(36)])
        self.sectors[id][0] = 1
        self.current_sector.append(0)
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
        """True if the car finished the circuit"""
        # print(self.sectors[player_id])
        for i in range(36):
            if self.sectors[player_id][i] == 0:
                return False
        return self.current_sector[player_id] == 0