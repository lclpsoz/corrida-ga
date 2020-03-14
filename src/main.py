import pygame
from controller_player import ControllerPlayer
from view import View

pygame.init()

config = {  'width' : 1200,
            'height': 600,
            'fps' : 60      }

game_now = ControllerPlayer(config)
game_now.run()

pygame.quit()