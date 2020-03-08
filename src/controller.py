import pygame
from car import car
from view import view

class controller(object):
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
        player = car(self.config['fps'], 100, 100)
        car_controls = car.get_controls()

        running = True
        while running:
            player.handle_keys()
            self.view.blit(player.draw(), player.get_pos())

            # Screen information
            text_pos_top_left = 0
            self.view.draw_car_controls(player.get_controls(), [0, 0])
            self.view.draw_player_data(self.get_player_data_str(player), [0, 60])
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
            