import pygame
import sys
import json
import random

sys.path.append('src')
from controller.controller_player import ControllerPlayer
from controller.controller_ai import ControllerAI
from view import View

pygame.init()

assert(len(sys.argv) > 1)
config = dict(json.load(open(sys.argv[1])))

if 'seed' in config:
    random.seed(config['seed'])
else:
    seed = random.randint(0, int(10**64-1))
    print("seed =", seed)
    random.seed(seed)

available_circuits = []
for x in config.keys():
    if str(x).startswith('circuit_'):
        available_circuits.append('_'.join(str(x).split('_')[1:]))
print("Available circuits:", available_circuits)

if len(sys.argv) > 2 and sys.argv[2] == 'ga':
    game_now = ControllerAI(config)
else:
    game_now = ControllerPlayer(config)
game_now.run()

pygame.quit()