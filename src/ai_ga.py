from ai import AI
import numpy as np
import random
import time
from copy import deepcopy

class AIGA(AI):
    def __init__(self, config):
        super(AIGA, self).__init__(config['ai']['population_size'])
        if self.population_size%2:
            print("Population size must be even!")
            exit(0)
        self.config = config
        self.gene_size = self.config['car']['number_of_visions'] + 1
        self.gene_amnt = 4 # Types of movement
        self.population = self.random_population(self.population_size)
        self.num_generations = config['ai']['num_of_generations']
        self.generation = 0
        self.verbose = config['verbose']
        self.t_gen_start = time.time()
        self.fps = config['fps']
        self.max_frames = config['ai']['max_frames']

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
            total = gene[0]*speed
            for j in range(1, self.gene_size):
                total += gene[j]*vision[j-1]
            mov.append(total >= 0)
        return mov

    def calc_fitness(self):
        """Calculate fitness of the population based on features."""
        self.fitness = []
        for i in range(self.population_size):
            feat = self.features[i]
            self.fitness.append(100*feat['perc_of_sectors'] +
                (self.max_frames - feat['amount_frames'])/self.fps)

    def next_generation(self):
        """If the number of generation was achieved, returns False, else,
        generates next generation."""
        self.generation += 1
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
        sorted_by_fitness = sorted(zip(self.fitness, self.features, self.population))
        if self.verbose > 0:
            print("Generation %d. Previous in %.2f s" % (self.generation, time.time() - self.t_gen_start))
            print("\tTOP 5% fitness:", ["%.2f, (%.2f, %.2f)" % (i[0], i[1]['perc_of_sectors'], i[1]['amount_frames']) for i in [(x,y) for x, y, _ in sorted_by_fitness][-int(self.population_size*0.05):]][::-1])
            print("\tBest fitness: %.2f" % max(self.fitness))
            print("\tAvr fitness: %.2f" % (sum(self.fitness)/self.population_size))
            print("\tWorst fitness: %.2f" % min(self.fitness))
        if self.verbose > 1:
            for i in range(self.population_size):
                print(self.population[i], self.features[i], self.fitness[i])
        if self.verbose > 0:
            print("")
        pop_elitism = deepcopy([x for _,_,x in sorted_by_fitness][-int(self.population_size*0.1):])
        pop_best_from_bef = deepcopy(random.choices(self.population, self.fitness, k=int(self.population_size*0.3)))
        pop_mutation = deepcopy(random.choices(self.population, self.fitness, k=int(self.population_size*0.3)))
        for i in range(len(pop_mutation)):
            for j in range(self.gene_amnt):
                for k in range(self.gene_size):
                    if random.random() < 0.1:
                        pop_mutation[i][j][k] += random.uniform(-0.1, 0.1) 
        pop_new = self.random_population(self.population_size - len(pop_elitism) - len(pop_best_from_bef) - len(pop_mutation))
        self.population = pop_elitism + pop_best_from_bef + pop_mutation + pop_new
        self.fitness = None
        self.evaluated = 0
        self.t_gen_start = time.time()

        return True