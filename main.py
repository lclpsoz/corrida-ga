import pygame
import sys
import json
import random
import os

sys.path.append('src')
from controller.controller_player import ControllerPlayer
from controller.controller_ai import ControllerAI
from interface import Interface

# Interface:
# python3 main.py
# Player Solo:
# python3 main.py src/config.json [track_name]
# GA visible trainning:
# python3 main.py src/config.json ga -v [track_name] [population_size]
# GA not visible trainning:
# python3 main.py src/config.json ga -notv [track_name] [population_size]
# reuse GA:
# python3 main.py src/config.json ga -notv -reuse [ga path] [generation]
# reuse GA in another circuit:
# python3 main.py src/config.json ga -notv -reuse [ga path] [generation] [track_name] [population_size]

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

    if len(sys.argv) > 4:
        # Specific GA and generation:
        if sys.argv[4] == '-reuse':
            config = json.load(open(os.path.join(sys.argv[5], 'config.json'), 'r'))
            ai_info = json.load(open(os.path.join(sys.argv[5], 'gen_' + sys.argv[6] + '.json'), 'r'))
            # Custom track:
            if len(sys.argv) > 7:
                config['track'] = sys.argv[7]
            #  Custom population size:
            if len(sys.argv) > 8:
                config['ai']['population_size'] = int(sys.argv[8])
        else:
            # Custom track:
            config['track'] = sys.argv[4]
            #  Custom population size:
            if len(sys.argv) > 5:
                config['ai']['population_size'] = int(sys.argv[5])

    # visibility
    if len(sys.argv) > 3:
        if sys.argv[3] == '-v':
            config['graphics'] = True
        elif sys.argv[3] == '-notv':
            config['graphics'] = False
        else:
            assert(False)
    
    if len(sys.argv) > 4 and sys.argv[4] == '-reuse':
        game_now = ControllerAI(config, ai_info)
    else:
        game_now = ControllerAI(config)
else:
    config['graphics'] = True
    if len(sys.argv) > 2:
        config['track'] = sys.argv[2]
    game_now = ControllerPlayer(config)
game_now.run()

pygame.quit()