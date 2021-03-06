import random
import time
import os
import json
import subprocess
import numpy as np
from copy import deepcopy
from datetime import datetime

class AIGA(object):
    def __init__(self, config, ai_info):
        self.population_size = config['ai']['population_size']
        self.config = config
        
        if (((not 'train' in self.config['ai']) or self.config['ai']['train']) and self.population_size%2):
            print("Population size must be even!")
            exit(0)
        
        self.evaluated = 0
        self.features = [None for x in range(self.population_size)]
        self.fitness = None
        self.population = None
        
        if 'save' in config['ai']:
            self.must_save = config['ai']['save']
        else:
            self.must_save = False
        
        # One for acc/break and the other for turns
        self.gene_amnt = 2
        self.gene_size = self.config['car']['number_of_visions'] + 1
        self.EPS = config['EPS']
        
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
        if not 'mutation_type' in config['ai'] or \
            config['ai']['mutation_type'] == 'simple':
            self.mutation = self.mutation_simple
        else:
            self.mutation = self.mutation_gradient

        self.mutation_chance = config['ai']['mutation_chance']
        self.mutation_factor = config['ai']['mutation_factor']
        self.pop_size_elitism = int(round(config['ai']["proportion_elitism"] * self.population_size))
        self.pop_size_crossover = int(round(config['ai']["proportion_crossover"] * self.population_size))
        if self.pop_size_crossover%2:
            self.pop_size_crossover -= 1
        self.pop_size_new = self.population_size - self.pop_size_crossover - self.pop_size_elitism

        try:
            label_last_commit = \
                subprocess.check_output(["git", "describe", "--always"]).strip()
            if isinstance(label_last_commit, bytes):
                label_last_commit = label_last_commit.decode('utf-8')
        except:
            label_last_commit = "_git-not_found"
        
        self.identifier = \
            "ga_" + \
            self.config["track"] + \
            datetime.now().strftime("__%Y-%d-%m_%H-%M-%S") + \
            "__git-" + label_last_commit
        if self.must_save:
            self.save()

    def set_evaluation(self, car_id : int, features : dict):
        """Set features of a car with car_id based on received features."""
        if self.features[car_id] == None:
            self.features[car_id] = features
            self.evaluated+=1

    def population_evaluated(self):
        """Returns if the whole population was evaluated."""
        return self.evaluated == self.population_size

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
            if feat['perc_of_sectors'] < 1.0-self.EPS:
                self.fitness.append(100*feat['perc_of_sectors'] +
                    (self.max_frames - feat['amount_frames'])/(2*self.max_frames))
            else:
                self.fitness.append(100*feat['perc_of_sectors'] +
                    (self.max_frames - feat['amount_frames']))
    
    def clamp(self, x, mini, maxi):
        """Apply clamp to x."""
        if x > maxi:
            return maxi
        elif x < mini:
            return mini
        return x
    
    def mutation_simple(self, indv):
        """Apply mutation to indv in place. Work by adding a random value in the
        interval [-self.mutation_factor, self.mutation_factor] to each position
        and aplying clamp so each value is in the range [-1, 1]."""
        for j in range(self.gene_amnt):
            for k in range(self.gene_size):
                if random.random() < self.mutation_chance:
                    indv[j][k] += random.uniform(-self.mutation_factor, self.mutation_factor)
                    self.clamp(indv[j][k], -1, 1)
                    
    def mutation_gradient(self, indv):
        """Apply mutation to indv in place. There's two type of mutation in this
        function, the first is applied to speed, and it's equivalent to
        mutation_simple, the second is for the rest of the gene, that is
        responsible for vision, and works by setting three points, left, center
        and right and applying a random value to this position that degredes
        as it is spread to all it neighbours."""
        for i in range(self.gene_amnt):
            indv[i][0] += random.uniform(-self.mutation_factor, self.mutation_factor)
            indv[i][0] = self.clamp(indv[i][0], -1, 1)

            left = 1
            if random.random() < self.mutation_chance:
                div = 1
                mut = random.uniform(-self.mutation_factor, self.mutation_factor)
                for j in range (left, self.gene_size):
                    indv[i][j] += mut/div
                    indv[i][j] = self.clamp(indv[i][j], -1, 1)
                    div *= 2

            center = self.config['car']['number_of_visions']//2 + 1
            if random.random() < self.mutation_chance:
                div = 1
                mut = random.uniform(-self.mutation_factor, self.mutation_factor)
                for j in range (center):
                    indv[i][center+j] += mut/div
                    indv[i][center+j] = self.clamp(indv[i][center+j], -1, 1)
                    if j:
                        indv[i][center-j] += mut/div
                        indv[i][center-j] = self.clamp(indv[i][center-j], -1, 1)
                    div *= 2

            right = self.config['car']['number_of_visions']
            if random.random() < self.mutation_chance:
                div = 1
                mut = random.uniform(-self.mutation_factor, self.mutation_factor)
                for j in range (right, left, -1):
                    indv[i][j] += mut/div
                    indv[i][j] = self.clamp(indv[i][j], -1, 1)
                    div *= 2

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

            self.mutation(indv)
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
        self.generation = ai_info['generation']
        self.features = [None for i in range(self.population_size)]
        self.fitness = None
        if len(ai_info['population']) >= self.population_size:
            self.population = ai_info['population'][-self.population_size:]
        else:
            sz_new = self.population_size - len(ai_info['population'])
            self.population = ai_info['population'] + self.random_population(sz_new)
        if len(self.population[0]) == 4:
            for i in range(len(self.population)):
                self.population[i][1] = self.population[i][2]
                self.population[i] = self.population[i][:2]

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

        if (not 'train' in self.config['ai']) or self.config['ai']['train']:
            pop_elitism = deepcopy([x for _,_,x in sorted_by_fitness][-self.pop_size_elitism:])[::-1]
            pop_crossover = []
            for i in range(0, self.pop_size_crossover, 2):
                parent_1, parent_2 = map(
                    deepcopy,
                    random.choices(self.population, self.fitness, k=2)
                )
                pop_crossover.extend(self.crossover(parent_1, parent_2))
            pop_new = self.random_population(self.pop_size_new)

            self.fitness = [x for x,_,_ in sorted_by_fitness]
            self.features = [x for _,x,_ in sorted_by_fitness]
            self.population = [x for _,_,x in sorted_by_fitness]

            if self.must_save:
                self.save()

            if self.verbose > 1:
                for i in range(self.population_size):
                    print(self.population[i], self.features[i], self.fitness[i])
            if self.verbose > 0:
                print("")
            self.population = pop_elitism + pop_crossover + pop_new
            self.generation += 1
        self.fitness = None
        self.features = [None for i in range(self.population_size)]
        self.evaluated = 0
        self.t_gen_start = time.time()


        return True