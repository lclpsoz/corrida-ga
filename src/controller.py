import pygame
from car import car
from view import view
from circuit_squared import circuitSquared
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import numpy as np

class controller():
    def __init__(self, config):
        self.view = view(config)
        self.config = config

    def get_player_data_str(self, player):
        """Builds a dict about the player car and returns it."""
        player_data = {}
        player_data['coord'] = str(player.get_pos())
        player_data['speed'] = str("%.2f" % player.get_speed()) + " m/s"
        player_data['dir'] = '(' + str("%.2f" % player.direction[0]) + ', ' + \
                                        str("%.2f" % player.direction[1]) + ')'
        return player_data
        
    def run(self):
        """Run game."""
        player = car(self.config['fps'], 600, 300)
        car_controls = car.get_controls()

        circuit = circuitSquared()
        circuit_surface = circuit.get_surface()

        running = True
        while running:
            self.view.blit(circuit_surface, [0, 0])
            player.handle_keys()
            player_surface = player.draw()
            self.view.blit(player_surface, player.get_pos_surface())

            # Check for collision
            collision = circuit.collision(player)

            # Screen information
            text_pos_top_left = 0
            self.view.draw_car_controls(player.get_controls(), [0, 0])
            self.view.draw_player_data(self.get_player_data_str(player), [0, 60])
            if(collision == 1):
                self.view.draw_text(0, 180, "Colliding with wall!", pygame.font.SysFont('mono', 20, bold=True), (255, 0, 0))
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
            