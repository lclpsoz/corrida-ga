import pygame
from car import Car
from view import View
from circuit_circle import CircuitCircle
from circuit_ellipse import CircuitEllipse
from circuit_squared import CircuitSquared
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import numpy as np
from datetime import datetime
import time

class Controller():
    def __init__(self, config):
        self.view = View(config)
        self.config = config

    def get_player_data_str(self, player):
        """Builds a dict about the player car and returns it."""
        player_data = {}
        player_data['coord'] = str(player.get_pos())
        player_data['speed'] = str("%.2f" % player.get_speed()) + " m/s"
        player_data['dir'] = '(' + str("%.2f" % player.direction[0]) + ', ' + \
                                        str("%.2f" % player.direction[1]) + ')'
        player_data['angle'] = str("%.2fº | %.2f rads" % (player.get_angle_degrees(), player.get_angle()))
        return player_data
        
    def reset(self, player, player_id, track):
        """Resets car and track."""
        player.reset()
        track.reset(player_id)

    def wait_key(self, key):
        """Wait for a specific pygame key. Still checks for exit keys."""
        while True:
            for event in pygame.event.get():
                if self.is_exit(event):
                    return False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    return True


    def is_exit(self, event):
        """Check if event is a exit event."""
        if event.type == pygame.QUIT:
            return True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return True
        return False

    def run(self):
        """Run game."""

        config_circuit_ellipse = {
            'center' : [self.config['width'] // 2, self.config['height'] // 2],
            'inner' : [150, 80],
            'outter' : [250, 170],
            'slow_area' : 20, 
            'wall' : 2,
            'slow_multiplier' : 20,
            'start_angle' : 90,
            'width' : self.config['width'],
            'height' : self.config['width']
        }

        config_circuit_circle = {
            'center' : [self.config['width'] // 2, self.config['height'] // 2],
            'inner_circle' : 150,
            'outter_circle' : 250, 
            'slow_area' : 20, 
            'wall' : 2,
            'slow_multiplier' : 20, 
            'start_angle' : 90,
            'width' : self.config['width'],
            'height' : self.config['height']
        }

        opt = input("0 for Circle Circuit or 1 for Ellipse Circuit: ")
        if opt == '0':
            track = CircuitCircle(config_circuit_circle)
        else:
            track = CircuitEllipse(config_circuit_ellipse)
        circuit_surface = track.draw()

        config_car = {
            'fps' : self.config['fps'],
            'x' : track.start[0],
            'y' : track.start[1],
            'start_angle' : track.start_angle,
            'number_of_visions' : 18,
            'vision_length' : 64,
            'car_vision_colors' : [(0, 254,0), (255, 0, 0)],
            'car_width' : 8,
            'car_height' : 16,
            'car_color' : (0, 0, 255),
            'front_color' : (0, 255, 255)
        }
        player = Car(config_car)
        car_controls = Car.get_controls()

        player_id = track.add_car(player)
        
        running = True
        while running:
            self.view.blit(circuit_surface, [0, 0])
            
            # Check for collision
            collision = track.collision_car(player)
            player.update_vision(track)

            if(collision == CircuitCircle.COLLISION_WALL):
                time_elapsed = datetime.fromtimestamp(track.get_current_time(player_id))
                str_time = time_elapsed.strftime("%M:%S:%f")
                print("Crashed! " + str_time)
                self.view.draw_text(self.config['width'] // 2 - 200, self.config['height'] // 2,
                    "Bateu!", pygame.font.SysFont('mono', 50, bold=True), (0, 255, 0))
                self.view.draw_text(self.config['width'] // 2 - 250, self.config['height'] // 2 + 50,
                    "Time: " + str_time, pygame.font.SysFont('mono', 40, bold=True), (120, 255, 0))
                self.view.draw_text(self.config['width'] // 2 - 370, self.config['height'] // 2 + 100,
                    "Pressione espaço para continuar!", pygame.font.SysFont('mono', 40, bold=True), (120, 255, 0))
                self.view.update()
                if self.wait_key(pygame.K_SPACE):
                    self.reset(player, player_id, track)
                else:
                    running = False
            elif(collision == CircuitCircle.COLLISION_SLOW_AREA):
                player.set_friction_multiplier(track.slow_friction_multiplier)
                player.handle_keys()
                self.view.draw_text(0, 180, "Dirigindo em area lenta!",
                    pygame.font.SysFont('mono', 20, bold=True), (255, 0, 0))
            else:
                player.set_friction_multiplier(1)
                player.handle_keys()

            player_surface = player.draw()
            track.update_sector(player_id, player)
            self.view.blit(player_surface, player.get_pos_surface())
            
            # Screen information
            text_pos_top_left = 0
            self.view.draw_text(0, 200, "Sector: " + str(track.current_sector[player_id]),
                pygame.font.SysFont('mono', 20, bold=True), (255, 0, 0))
            self.view.draw_car_controls(player.get_controls(), [0, 0])
            self.view.draw_player_data(self.get_player_data_str(player), [0, 60])
            
            # tantantan tantantan
            if track.finished(player_id):
                time_elapsed = datetime.fromtimestamp(track.get_current_time(player_id))
                str_time = time_elapsed.strftime("%M:%S:%f")
                print("Finished the track! " + str_time)
                self.view.draw_text(self.config['width'] // 2 - 200, self.config['height'] // 2,
                    "Acabou!", pygame.font.SysFont('mono', 50, bold=True), (0, 255, 0))
                self.view.draw_text(self.config['width'] // 2 - 250, self.config['height'] // 2 + 50,
                    "Time: " + str_time, pygame.font.SysFont('mono', 40, bold=True), (120, 255, 0))
                self.view.draw_text(self.config['width'] // 2 - 370, self.config['height'] // 2 + 100,
                    "Pressione espaço para continuar!", pygame.font.SysFont('mono', 40, bold=True), (120, 255, 0))
                self.view.update()
                if self.wait_key(pygame.K_SPACE):
                    self.reset(player, player_id, track)
                else:
                    running = False

            self.view.update()

            # Events
            for event in pygame.event.get():
                if self.is_exit(event):
                    running = False
            