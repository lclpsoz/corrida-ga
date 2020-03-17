import pygame
from controller_player import ControllerPlayer
from controller_ai import ControllerAI
from view import View
import sys
import json

pygame.init()

assert(len(sys.argv) > 1)
config = json.load(open(sys.argv[1]))

if len(sys.argv) > 1 and sys.argv[2] == 'ga':
    game_now = ControllerAI(config)
else:
    game_now = ControllerPlayer(config)
game_now.run()

pygame.quit()