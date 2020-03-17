import pygame
from controller_player import ControllerPlayer
from controller_ai import ControllerAI
from view import View
import sys
import json
import random

pygame.init()

assert(len(sys.argv) > 1)
config = json.load(open(sys.argv[1]))

if 'seed' in config:
    random.seed(config['seed'])
else:
    seed = random.randint(0, int(10**64-1))
    print("seed =", seed)
    random.seed(seed)

if len(sys.argv) > 1 and sys.argv[2] == 'ga':
    game_now = ControllerAI(config)
else:
    game_now = ControllerPlayer(config)
game_now.run()

pygame.quit()