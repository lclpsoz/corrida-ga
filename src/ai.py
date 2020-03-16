from abc import ABCMeta, abstractmethod

class AI(metaclass=ABCMeta):
    def __init__(self, population_size):
        self.population_size = population_size
        self.evaluated = 0
        self.features = [None for x in range(population_size)]
        self.fitness = None
        self.population = None

    @abstractmethod
    def calc_movement(self, car_id : int, vision : list):
        """Based on car with car_id AI and it vision at the moment,
        returns movement list."""
        pass

    def set_evaluation(self, car_id : int, features : dict):
        """Set features of a car with car_id based on received features."""
        self.features[car_id] = features
        self.evaluated+=1

    def population_evaluated(self):
        """Returns if the whole population was evaluated."""
        return self.evaluated == self.population_size