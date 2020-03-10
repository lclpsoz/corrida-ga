from abc import ABCMeta, abstractmethod
from shapely.geometry.polygon import Polygon

class Circuit(metaclass=ABCMeta):
    COLLISION_NONE = 0
    COLLISION_SLOW_AREA = 1
    COLLISION_WALL = 2
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def collision(self, shape):
        """Returns the type of collision of the shapely shape and the circuit.
        Can be NONE, SLOW_AREA or WALL."""
        pass

    @abstractmethod
    def draw(self):
        """Returns the pygame.Surface with the track drawed."""
        pass

    def collision_car(self, player):
        """Returns the type of collision of the car and the circuit. Can be
        NONE, SLOW_AREA or WALL."""
        return self.collision(Polygon(player.get_points()))

    def get_points_shape(self, shape):
        """Receives any shapely shape and returns it points in a array"""
        if isinstance(shape, Polygon):
            shape = shape.exterior
        xy = shape.coords.xy
        points = [(xy[0][i], xy[1][i]) for i in range(len(xy[0]))]
        return points