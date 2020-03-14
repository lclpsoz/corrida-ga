import pygame
from controller_player import ControllerPlayer
from controller_ai import ControllerAI
from view import View
import sys

pygame.init()

config = {  'width' : 1200,
            'height': 600,
            'fps' : 60      }

if len(sys.argv) > 1 and sys.argv[1] == 'ga':
    game_now = ControllerAI(config)
else:
    game_now = ControllerPlayer(config)
game_now.run()

pygame.quit()