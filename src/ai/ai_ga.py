import random
import time
import os
import json
import numpy as np
from copy import deepcopy
from datetime import datetime

from ai.ai import AI

class AIGA(AI):
    def __init__(self, config, ai_info):
        super(AIGA, self).__init__(config['ai']['population_size'])
        if self.population_size%2:
            print("Population size must be even!")
            exit(0)
        self.config = config
        self.EPS = config['EPS']
        self.gene_size = self.config['car']['number_of_visions'] + 1
        self.gene_amnt = 4 # Types of movement
        if ai_info:
            self.set_ai_info(ai_info)
        else:
            self.population = self.random_population(self.population_size)
            self.generation = 1
        self.num_generations = config['ai']['num_of_generations']
        self.verbose = config['verbose']
        self.t_gen_start = time.time()
        self.fps = config['fps']
        if 'max_frames' in config['ai']:
            self.max_frames = config['ai']['max_frames']
        else:
            self.max_frames = config["circuit_" + config['track']]['max_frames']
        self.mutation_chance = config['ai']['mutation_chance']
        self.mutation_factor = config['ai']['mutation_factor']
        self.pop_size_elitism = int(round(config['ai']["proportion_elitism"] * self.population_size))
        self.pop_size_crossover = int(round(config['ai']["proportion_crossover"] * self.population_size))
        if self.pop_size_crossover%2:
            self.pop_size_crossover -= 1
        self.pop_size_new = self.population_size - self.pop_size_crossover - self.pop_size_elitism

        self.identifier = "ga_" + self.config["track"] + datetime.now().strftime("__%Y-%d-%m_%H-%M-%S")
        self.save()

    def random_population(self, n):
        """Generate n random individuals."""
        ret = []
        for i in range(n):
            ret.append([[random.uniform(-1, 1) for j in range(self.gene_size)]
                            for i in range(self.gene_amnt)])

        return ret

    def calc_movement(self, car_id, vision, speed):
        """Based on car with car_id AI, it's vision and speed at the moment,
        returns movement list."""
        mov = []
        indv = self.population[car_id]
        for i in range(self.gene_amnt):
            gene = indv[i]
            total = (gene[0]*speed)/self.config['car']['number_of_visions']
            for j in range(1, self.gene_size):
                total += gene[j]*vision[j-1]
            mov.append(total)
        return mov

    def calc_fitness(self):
        """Calculate fitness of the population based on features."""
        self.fitness = []
        for i in range(self.population_size):
            feat = self.features[i]
            self.fitness.append(100*feat['perc_of_sectors'] +
                (self.max_frames - feat['amount_frames'])/(2*self.max_frames))

    def mutation(self, indv):
        """Apply mutation to indv in place."""
        for j in range(self.gene_amnt):
            for k in range(self.gene_size):
                if random.random() < self.mutation_chance:
                    indv[j][k] += random.uniform(-self.mutation_factor, self.mutation_factor)
                    if indv[j][k] > 1:
                        indv[j][k] = 1
                    elif indv[j][k] < -1:
                        indv[j][k] = -1

    def crossover(self, parent_1, parent_2):
        """Returns two individuals, result of the crossover."""
        # Proportion from each parent
        proportion_vision = random.randint(0, self.gene_size//2)
        mid_left = (self.gene_size-2)//2 - proportion_vision
        mid_right = (self.gene_size-1)//2 + proportion_vision
        dominant_speed = random.randint(0, 1)
        
        def apply(p_1, p_2):
            """Apply crossover."""
            indv = deepcopy(p_1)
            for i in range(self.gene_amnt):
                if not dominant_speed:
                    indv[i][0] = p_2[i][0]
                for k in range(mid_left+1, mid_right):
                    indv[i][k] = p_2[i][k]

            return indv

        return [apply(parent_1, parent_2),
                apply(parent_2, parent_1)]

    def save(self):
        """Save data about the AI in specific folder."""
        folder_path = os.path.join("ga", self.identifier)
        if not os.path.exists("ga"):
            os.makedirs("ga")
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        file_path = os.path.join(
            folder_path,
            "config.json"
        )
        if self.generation == 0 or not os.path.exists(file_path):
            json.dump(self.config, open(file_path, 'w'))
        else:
            ai_info = {
                'population' : self.population,
                'generation' : self.generation,
                'features' : self.features,
                'fitness' : self.fitness
            }
            file_path = os.path.join(
                folder_path,
                "gen_" + str(self.generation) + ".json"
            )
            json.dump(ai_info, open(file_path, 'w'))

    def load_generation(self, ga_folder_path : str, generation : int):
        """Loads specified generation from folder ga_folder_path."""
        load(os.path.join(ga_folder_path, "gen_" + str(generation)))

    def load(self, file_path):
        """Loads generation saved on json in file_path."""
        self.load(json.load(open(file_path, 'r')))

    def set_ai_info(self, ai_info):
        """Sets attributes of class based on ai_info."""
        self.population = ai_info['population']
        self.generation = ai_info['generation']
        self.features = ai_info['features']
        self.fitness = ai_info['fitness']

    def next_generation(self):
        """If the number of generation was achieved, returns False, else,
        generates next generation."""
        if self.generation == self.num_generations:
            if self.verbose > 0:
                print("Generation %d. Previous in %.2f s" % (self.generation, time.time() - self.t_gen_start))
            if self.verbose > 1:
                print("Last generation:")
                for i in range(len(self.population)):
                    print(self.population[i], self.features[i])
            if self.verbose > 0:
                print("")

            return False

        self.calc_fitness()
        sorted_by_fitness = list(zip(self.fitness, self.features, self.population))
        sorted_by_fitness.sort(key=lambda x : (x[0], x[2]))
        if self.verbose > 0:
            print("Generation %d. Evaluated in %.2f s" % (
                self.generation,
                time.time() - self.t_gen_start)
            )
            qnt_top_5p = max(1, int(self.population_size*0.05))
            top_5p = [(x,y) for x, y, _ in sorted_by_fitness][-qnt_top_5p:]
            to_prt = [( x[0],
                        x[1]['perc_of_sectors'],
                        x[1]['amount_frames']) for x in top_5p][::-1]
            print("\tTOP 5% fitness:", ["%.2f, (%.2f, %.2f)" % x for x in to_prt])
            print("\tBest fitness: %.2f" % max(self.fitness))
            print("\tAvr fitness: %.2f" % (sum(self.fitness)/self.population_size))
            print("\tWorst fitness: %.2f" % min(self.fitness))

        pop_elitism = deepcopy([x for _,_,x in sorted_by_fitness][-self.pop_size_elitism:])[::-1]
        pop_crossover = []
        for i in range(0, self.pop_size_crossover, 2):
            parent_1, parent_2 = map(
                deepcopy,
                random.choices(self.population, self.fitness, k=2)
            )
            pop_crossover.extend(self.crossover(parent_1, parent_2))
        pop_new = self.random_population(self.pop_size_new)

        self.save()

        self.population = pop_elitism + pop_crossover + pop_new
        self.fitness = None
        self.features = [None for i in range(self.population_size)]
        self.evaluated = 0
        self.t_gen_start = time.time()
        self.generation += 1

        if self.verbose > 1:
            for i in range(self.population_size):
                print(self.population[i], self.features[i], self.fitness[i])
        if self.verbose > 0:
            print("")

        return True