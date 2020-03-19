import pygame
from car import Car
from view import View
from controller import Controller
from circuit_custom import CircuitCustom
from circuit_circle import CircuitCircle
from circuit_ellipse import CircuitEllipse
from circuit_maker import CircuitMaker
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import numpy as np
from datetime import datetime
import time

class ControllerPlayer(Controller):
    def __init__(self, config):
        super(Controller, self).__init__()
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
                if event.type == pygame.KEYDOWN and event.key == key:
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
        x_track_offset = self.config['width']//3
        self.start_track()
        self.start_car()

        circuit_surface = self.track.draw()

        player = Car(self.config_car)
        car_controls = Car.get_controls()

        player_id = self.track.add_car(player, self.view.num_frame)

        running = True
        while running:
            self.view.blit(circuit_surface, [x_track_offset, 0])
            
            # Check for collision
            collision = self.track.collision_car(player)
            player.update_vision(self.track)

            if(collision == CircuitCircle.COLLISION_WALL):
                time_elapsed = datetime.fromtimestamp(self.track.get_current_car_time(player_id))
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
                    self.reset(player, player_id, self.track)
                else:
                    running = False
            elif(collision == CircuitCircle.COLLISION_SLOW_AREA):
                player.set_friction_multiplier(self.track.slow_friction_multiplier)
                player.handle_keys()
                self.view.draw_text(0, 180, "Dirigindo em area lenta!",
                    pygame.font.SysFont('mono', 20, bold=True), (255, 0, 0))
            else:
                player.set_friction_multiplier(1)
                player.handle_keys()
            player.apply_movement()

            player_surface = player.draw()
            self.track.update_car_sector(player_id, player)
            self.view.blit(player_surface, player.get_pos_surface())
            
            # self.view.draw_car_controls(player.get_controls(), [0, 0])
            # self.view.draw_player_data(self.get_car_data_str(player), [0, 60])
            
            # tantantan tantantan
            if self.track.finished(player_id):
                time_elapsed = datetime.fromtimestamp(self.track.get_current_car_time(player_id))
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
                    self.reset(player, player_id, self.track)
                else:
                    running = False

            self.view.update()

            # Events
            for event in pygame.event.get():
                if self.is_exit(event):
                    running = False