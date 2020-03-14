import pygame
from car import Car
from view import View
from circuit_circle import CircuitCircle
from circuit_ellipse import CircuitEllipse
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import numpy as np
from datetime import datetime
from functools import partial
import time

class ControllerAI():
    def __init__(self, config):
        self.view = View(config)
        self.config = config

    def get_car_data_str(self, car):
        """Builds a dict about the car car and returns it."""
        car_data = {}
        car_data['coord'] = str(car.get_pos())
        car_data['speed'] = str("%.2f" % car.get_speed()) + " m/s"
        car_data['dir'] = '(' + str("%.2f" % car.direction[0]) + ', ' + \
                                        str("%.2f" % car.direction[1]) + ')'
        car_data['angle'] = str("%.2fº | %.2f rads" % (car.get_angle_degrees(), car.get_angle()))
        return car_data
        
    def reset(self, car, car_id, track):
        """Resets car and track."""
        car.reset()
        track.reset(car_id)

    def wait_key(self, key):
        """Wait for a specific pygame key. Still checks for exit keys."""
        while True:
            for event in pygame.event.get():
                if self.is_exit(event):
                    return False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    return True


    def is_exit(self, event):
        """Check if event is a exit event."""
        if event.type == pygame.QUIT:
            return True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return True
        return False

    def ai_manual(self, vision_range_size, mov_free, mov_blocked, car):
        """Manually programmed AI. The vision_range_size determines the amount
        of vision segments that will be considered when deciding if the movement
        is free or blocked."""
        mid = len(car.vision)//2
        left = mid - vision_range_size//2
        right = mid + vision_range_size//2 + 1
        if not any(car.vision[left : right]):
            car.movement = mov_free
        else:
            car.movement = mov_blocked

    def run(self):
        """Run project."""
        config_circuit_ellipse = {
            'center' : [self.config['width'] // 2, self.config['height'] // 2],
            'inner' : [150, 80],
            'outter' : [250, 170],
            'slow_area' : 20, 
            'wall' : 2,
            'slow_multiplier' : 10,
            'start_angle' : 90,
            'width' : self.config['width'],
            'height' : self.config['width']
        }

        config_circuit_circle = {
            'center' : [self.config['width'] // 2, self.config['height'] // 2],
            'inner_circle' : 150,
            'outter_circle' : 250, 
            'slow_area' : 20, 
            'wall' : 2,
            'slow_multiplier' : 10, 
            'start_angle' : 90,
            'width' : self.config['width'],
            'height' : self.config['height']
        }

        opt = input("0 for Circle Circuit or 1 for Ellipse Circuit: ")
        if opt == '0':
            track = CircuitCircle(config_circuit_circle)
        else:
            track = CircuitEllipse(config_circuit_ellipse)
        circuit_surface = track.draw()

        config_car = {
            'fps' : self.config['fps'],
            'x' : track.start[0],
            'y' : track.start[1],
            'start_angle' : track.start_angle,
            'number_of_visions' : 18,
            'vision_length' : 64,
            'car_vision_colors' : [(0, 254,0), (255, 0, 0)],
            'car_width' : 8,
            'car_height' : 16,
            'car_color' : (0, 0, 255),
            'front_color' : (0, 255, 255)
        }
        config_car_2 = config_car.copy()
        config_car_2['car_color'] = (255, 0, 0)
        config_car_3 = config_car.copy()
        config_car_3['car_color'] = (0, 255, 255)
        config_car_4 = config_car.copy()
        config_car_4['car_color'] = (255, 125, 0)
        config_car_5 = config_car.copy()
        config_car_5['car_color'] = (125, 0, 255)
        cars = [Car(config_car),
                Car(config_car_2),
                Car(config_car_3),
                Car(config_car_4),
                Car(config_car_5)]
        cars_id = []
        for car in cars:
            cars_id.append(track.add_car(car))
        cars_ai = [partial(self.ai_manual, 1, [1, 0, 0, 0], [0, 1, 0, 1]),
                    partial(self.ai_manual, 3, [1, 0, 0, 0], [0, 1, 0, 1]),
                    partial(self.ai_manual, 5, [1, 0, 0, 0], [0, 1, 0, 1]), # Accelerates OR (Turn Right AND Breaks)
                    partial(self.ai_manual, 5, [1, 0, 0, 0], [0, 0, 0, 1]), # Accelerates OR Turn Right
                    partial(self.ai_manual, 5, [1, 0, 0, 0], [1, 0, 0, 1])] # Accelerates OR (Accelerates AND Turn Right)
        
        running = True
        while running:
            self.view.blit(circuit_surface, [0, 0])
            
            for i in range(len(cars)):
                car = cars[i]
                car_id = cars_id[i]
                car_ai = cars_ai[i]

                collision = track.collision_car(car)
                car.update_vision(track)

                car_ai(car)

                if(collision == CircuitCircle.COLLISION_WALL):
                    self.reset(car, car_id, track)
                elif(collision == CircuitCircle.COLLISION_SLOW_AREA):
                    car.set_friction_multiplier(track.slow_friction_multiplier)
                else:
                    car.set_friction_multiplier(1)
                car.apply_movement()

                car_surface = car.draw()
                track.update_sector(car_id, car)
                self.view.blit(car_surface, car.get_pos_surface())
                
                if track.finished(car_id):
                    self.reset(car, car_id, track)

            self.view.update()

            # Events
            for event in pygame.event.get():
                if self.is_exit(event):
                    running = False