import pygame
from car import Car
from view import View
from circuit_circle import CircuitCircle
from circuit_squared import CircuitSquared
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import numpy as np
import time
from datetime import datetime

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
        
    def run(self):
        """Run game."""

        track = CircuitCircle([self.config['width'] // 2, self.config['height'] // 2])
        circuit_surface = track.draw()

        player = Car(self.config['fps'], track.start[0], track.start[1])
        car_controls = Car.get_controls()

        player_id = track.add_player(player)

        # here or in the car class?
        start_time = time.time()

        running = True
        while running:
            self.view.blit(circuit_surface, [0, 0])
            player.handle_keys()
            player_surface = player.draw()
            self.view.blit(player_surface, player.get_pos_surface())
            
            track.update_sector(player_id, player)
            
            # tantantan tantantan
            if track.finished(player_id):
                time_elapsed = datetime.fromtimestamp(time.time() - start_time)
                str_time = time_elapsed.strftime("%M:%S:%f")
                print("GG! " + str_time)
                self.view.draw_text(self.config['width'] // 2 - 200, self.config['height'] // 2, "CABOU CARAI", pygame.font.SysFont('mono', 50, bold=True), (0, 255, 0))
                self.view.draw_text(self.config['width'] // 2 - 250, self.config['height'] // 2 + 50, "Time: " + str_time, pygame.font.SysFont('mono', 40, bold=True), (120, 255, 0))
                running = False

            # Check for collision
            collision = track.collision_car(player)

            # Screen information
            text_pos_top_left = 0
            self.view.draw_text(0, 200, "Sector: " + str(track.current_sector[player_id]), pygame.font.SysFont('mono', 20, bold=True), (255, 0, 0))
            self.view.draw_car_controls(player.get_controls(), [0, 0])
            self.view.draw_player_data(self.get_player_data_str(player), [0, 60])
            if(collision == CircuitCircle.COLLISION_WALL):
                self.view.draw_text(0, 180, "Colliding with wall!", pygame.font.SysFont('mono', 20, bold=True), (255, 0, 0))
            elif(collision == CircuitCircle.COLLISION_SLOW_AREA):
                self.view.draw_text(0, 180, "Driving on slow area!", pygame.font.SysFont('mono', 20, bold=True), (255, 0, 0))
            
            self.view.update()

            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        break
            