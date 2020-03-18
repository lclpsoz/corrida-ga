import pygame
from car import Car
from view import View
from circuit_circle import CircuitCircle
from circuit_ellipse import CircuitEllipse
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import numpy as np
from datetime import datetime
import time

class ControllerPlayer():
    def __init__(self, config):
        self.view = View(config)
        self.config = config

    def get_car_data_str(self, car):
        """Builds a dict about the car car and returns it."""
        car_data = {}
        car_data['coord'] = str(car.get_pos())
        car_data['speed'] = str("%.2f" % car.get_speed()) + " m/s"
        car_data['dir'] = '(' + str("%.2f" % car.direction[0]) + ', ' + \
                                        str("%.2f" % car.direction[1]) + ')'
        car_data['angle'] = str("%.2fº | %.2f rads" % (car.get_angle_degrees(), car.get_angle()))
        return car_data
        
    def reset(self, car, car_id, track):
        """Resets car and track."""
        car.reset()
        track.reset(car_id, self.view.num_frame)

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
        """Run project."""
        if self.config['track'] == 'circle':
            track = CircuitCircle(self.config)
        else:
            track = CircuitEllipse(self.config)
        circuit_surface = track.draw()

        config_car = self.config['car']
        config_car.update({
            'fps' : self.config['fps'],
            'x' : track.start[0],
            'y' : track.start[1],
            'start_angle' : track.start_angle,
        })
        player = Car(config_car)
        car_controls = Car.get_controls()

        player_id = track.add_car(player, self.view.num_frame)
        
        running = True
        while running:
            self.view.blit(circuit_surface, [0, 0])
            
            # Check for collision
            collision = track.collision_car(player)
            player.update_vision(track)

            if(collision == CircuitCircle.COLLISION_WALL):
                time_elapsed = datetime.fromtimestamp(track.get_current_car_time(player_id))
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
            player.apply_movement()

            player_surface = player.draw()
            track.update_car_sector(player_id, player)
            self.view.blit(player_surface, player.get_pos_surface())
            
            # Screen information
            text_pos_top_left = 0
            self.view.draw_text(0, 200, "Sector: " + str(track.car_current_sector[player_id]),
                pygame.font.SysFont('mono', 20, bold=True), (255, 0, 0))
            self.view.draw_car_controls(player.get_controls(), [0, 0])
            self.view.draw_player_data(self.get_car_data_str(player), [0, 60])
            
            # tantantan tantantan
            if track.finished(player_id):
                time_elapsed = datetime.fromtimestamp(track.get_current_car_time(player_id))
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