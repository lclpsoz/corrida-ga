import pygame
import sys
import json
import random
import os

sys.path.append('src')
from controller.controller_player import ControllerPlayer
from controller.controller_ai import ControllerAI
from interface import Interface

# Exemple of command to reuse GA:
# python3 main.py src/config.json ga rect_rounded 100 ga/ga_rect_rounded__2020-22-03_14-48-07 32

pygame.init()

if len(sys.argv) == 1:
    Interface().run()
    exit(0)

config = dict(json.load(open(sys.argv[1])))

if 'seed' in config:
    random.seed(config['seed'])
else:
    seed = random.randint(0, int(2**64-1))
    print("seed =", seed)
    random.seed(seed)

available_circuits = []
for x in config.keys():
    if str(x).startswith('circuit_'):
        available_circuits.append('_'.join(str(x).split('_')[1:]))
print("Available circuits:", available_circuits)

if len(sys.argv) > 2 and sys.argv[2] == 'ga':
    # Custom track:
    if len(sys.argv) > 3:
        config['track'] = sys.argv[3]

    # Custom population size:
    if len(sys.argv) > 4:
        config['ai']['population_size'] = int(sys.argv[4])

    # Specific GA and generation:
    if len(sys.argv) > 6:
        config = json.load(open(os.path.join(sys.argv[5], 'config.json'), 'r'))
        ai_info = json.load(open(os.path.join(sys.argv[5], 'gen_' + sys.argv[6] + '.json'), 'r'))
    game_now = ControllerAI(config, ai_info)
else:
    game_now = ControllerPlayer(config)
game_now.run()

pygame.quit()