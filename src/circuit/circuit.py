from abc import ABCMeta, abstractmethod
from shapely.geometry.polygon import Polygon
import time

class Circuit(metaclass=ABCMeta):
    COLLISION_NONE = 0
    COLLISION_SLOW_AREA = 1
    COLLISION_WALL = 2
    @abstractmethod
    def __init__(self, config):
        self.slow_area = config['slow_area']
        self.wall = config['wall']
        self.start_angle = config['start_angle']
        self.slow_friction_multiplier = config['slow_multiplier']
        self.color_background = (255,255,255)
        self.color_wall = (0,0,0)
        self.color_slow_area = (220,220,220)
        self.num_of_sectors = None
        self.car_start_time = []
        self.car_sectors = []
        self.car_current_sector = []
        self.car_start_frame = []
    
    @abstractmethod
    def collision(self, shape):
        """Returns the type of collision of the shapely shape and the circuit.
        Can be NONE, SLOW_AREA or WALL."""
        pass

    @abstractmethod
    def draw(self):
        """Returns the pygame.Surface with the track drawed."""
        pass

    @abstractmethod
    def update_car_sector(self, car_id, player):
        """Updates the sector of the car."""
        pass

    def add_car(self, player, frame_now):
        """Adds a car in the circuit."""
        id = len(self.car_sectors)
        self.car_sectors.append([0 for i in range(self.num_of_sectors)])
        self.car_sectors[id][0] = 1
        self.car_current_sector.append(0)
        self.car_start_time.append(time.time())
        self.car_start_frame.append(frame_now)

        return id
    
    def reset(self, car_id, frame_now):
        """Reset car with car_id."""
        self.car_sectors[car_id] = [0 for i in range(self.num_of_sectors)]
        self.car_sectors[car_id][0] = 1
        self.car_current_sector[car_id] = 0
        self.car_start_time[car_id] = time.time()
        self.car_start_frame[car_id] = frame_now

    def finished(self, car_id):
        """True if the car finished the circuit, False otherwise."""
        return sum(self.car_sectors[car_id]) == self.num_of_sectors

    def collision_car(self, car):
        """Returns the type of collision of the car and the circuit. Can be
        NONE, SLOW_AREA or WALL."""
        return self.collision(Polygon(car.get_points()))

    def batch_collision_car(self, list_cars):
        """Returns a list of types of collisions, each position corresponding
        to each car in list_cars."""
        return [self.collision_car(car) for car in list_cars]        

    def batch_collision(self, list_shapes : list):
        """Returns a list of types of collisions, each position corresponding
        to each shape in list_shapes."""
        return [self.collision(shape) for shape in list_shapes] 

    def get_points_shape(self, shape):
        """Receives any shapely shape and returns it points in a array"""
        if isinstance(shape, Polygon):
            shape = shape.exterior
        xy = shape.coords.xy
        points = [(xy[0][i], xy[1][i]) for i in range(len(xy[0]))]
        return points

    def get_current_car_time(self, car_id):
        """Returns current time by car with car_id."""
        return time.time() - self.car_start_time[car_id]

    def get_car_num_frames(self, car_id, frame_now):
        """Returns number of frames since the car was added."""
        return frame_now - self.car_start_frame[car_id]

    def get_car_perc_sectors(self, car_id):
        """Returns percentage of sectors already traversed by car with car_id."""
        return sum(self.car_sectors[car_id])/self.num_of_sectors