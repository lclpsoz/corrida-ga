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
# python3 main.py src/config.json -player
# GA not visible trainning:
# python3 main.py src/config.json -notv
# !!Warning!! When using -reuse, must use it just after config.json, otherwise
# it will overwrite the commands before.
# reuse GA:
# python3 main.py src/config.json -reuse [ga path] [generation]
# reuse GA in another circuit:
# python3 main.py src/config.json -reuse [ga path] [generation] -track [track_name]

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

options = {
    '-track' : ['track', str],
    '-fps' : ['fps', int],
    '-pop_sz' : ['ai', 'population_size', int],
    '-mut_type' : ['ai', 'mutation_type', str],
    '-mut_chance' : ['ai', 'mutation_chance', float],
    '-mut_factor' : ['ai', 'mutation_factor', float],
    '-num_gen' : ['ai', 'num_of_generations', int],
    '-max_frames' : ['ai', 'max_frames', int],

    '-player' : ['PLAYER'],
    '-reuse' : ['LOAD'],
    '-tv' : ['SET', 'graphics', True],
    '-notv' : ['SET', 'graphics', False],
    '-save' : ['SET', 'ai', 'save', True],
    '-nosave' : ['SET', 'ai', 'save', False]
}

game_now = "GA"
i = 2
while i < len(sys.argv):
    now = options[sys.argv[i]]
    if now[0] == 'PLAYER':
        game_now = "PLAYER"
    elif now[0] == 'LOAD':
        config = json.load(open(os.path.join(sys.argv[i+1], 'config.json'), 'r'))
        ai_info = json.load(open(os.path.join(sys.argv[i+1], 'gen_' + sys.argv[i+2] + '.json'), 'r'))
        config['reuse'] = sys.argv[i+1]
        game_now = "GA_INFO"
        i += 2
    elif now[0] == 'SET':
        cnf = config
        for j in range(1, len(now)-2):
            cnf = cnf[now[j]]
        cnf[now[-2]] = now[-1]
    else:
        cnf = config
        for j in range(0, len(now)-2):
            cnf = cnf[now[j]]
        cnf[now[-2]] = now[-1](sys.argv[i+1])
        i+=1
    i+=1
if game_now == "GA":
    game_now = ControllerAI(config)
elif game_now == "GA_INFO":
    game_now = ControllerAI(config, ai_info)
else:
    config['graphics'] = True
    game_now = ControllerPlayer(config)

game_now.run()

pygame.quit()