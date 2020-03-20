import random
import time

from ai.ai import AI

class AIManual(AI):
    def __init__(self, config):
        super(AIManual, self).__init__(config['ai']['population_size'])
        self.population = [random.random() for x in range(self.population_size)]
        self.num_generations = config['ai']['num_of_generations']
        self.generation = 0
        self.else_moves = [[0, 0] for x in range(self.population_size)]
        self.verbose = config['verbose']
        self.t_gen_start = time.time()

    def calc_movement(self, car_id, vision, speed):
        """Based on car with car_id AI and it vision at the moment,
        returns movement list."""
        return self.ai_heur(
            5,
            [1, 0, 0, 0],
            self.population[car_id],
            [0, 0, 0, 1],
            [1, 0, 0, 1],
            vision,
            car_id
        )

    def ai_heur(self, vision_range_size, mov_free, odd_mov_1, mov_blocked_1,
                    mov_blocked_2, vision, car_id = None):
        """Manually programmed AI. The vision_range_size determines the amount
        of vision segments that will be considered when deciding if the movement
        is free or blocked. There's a chance of odd_mov_1 that mov_blocked_1 will
        be applied and 1 - odd_mov_1 that mov_blocked_2 will be."""
        mid = len(vision)//2
        left = mid - vision_range_size//2
        right = mid + vision_range_size//2 + 1
        if not any(vision[left : right]):
            return mov_free
        else:
            if self.else_moves[car_id][1] and \
                self.else_moves[car_id][0]/sum(self.else_moves[car_id]) < odd_mov_1:
                
                if car_id != None:
                    self.else_moves[car_id][0] += 1
                return mov_blocked_1
            else:
                if car_id != None:
                    self.else_moves[car_id][1] += 1
                return mov_blocked_2
    
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
        old_population = []
        for i in range(self.population_size):
            old_population.append((self.population[i], self.features[i]))
        old_population.sort(key=lambda x : (-x[1]['perc_of_sectors'], x[1]['amount_frames']))

        # Reset
        self.evaluated = 0
        self.features = [None for x in range(self.population_size)]
        self.else_moves = [[0, 0] for x in range(self.population_size)]
        mini = 1.0
        maxi = 0.0
        for i in range(int(0.2*self.population_size)):
            mini = min(mini, old_population[i][0])
            maxi = max(maxi, old_population[i][0])
        if self.verbose > 0:
            print("Generation %d. Previous in %.2f s" % (self.generation, time.time() - self.t_gen_start))
            print("\tBest 20%%: [%.5f, %.5f]" % (mini, maxi))
        if self.verbose > 1:
            print(old_population)
        if self.verbose > 0:
            print("")
        mini = max(0.0, mini-(random.random()*(0.1/self.population_size)))
        maxi = min(1.0, maxi+(random.random()*(0.1/self.population_size)))
        self.population = [random.uniform(mini, maxi) for x in range(self.population_size-1)]
        self.population.append(old_population[0][0]) # The best from the previous generation
        self.t_gen_start = time.time()

        return True