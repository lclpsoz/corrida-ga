import pygame
from car import Car
from view import View
from circuit_circle import CircuitCircle
from circuit_ellipse import CircuitEllipse
from ai_manual import AIManual
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import numpy as np
from datetime import datetime
from functools import partial
import random
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
        track.reset(car_id, self.view.num_frame)

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

        num_of_cars = 100
        ai = AIManual(num_of_cars, 20)
        
        cars = []
        cars_colors = random.sample(pygame.color.THECOLORS.items(), k=num_of_cars)
        while(len(cars) < num_of_cars):
            config_car_now = config_car.copy()
            config_car_now['car_color'] = cars_colors.pop()[1]
            cars.append({})
            cars[-1]['car'] = Car(config_car_now)
            cars[-1]['id'] = track.add_car(cars[-1], self.view.num_frame)
            cars[-1]['name'] = "ai_heur_%.3f" % ai.population[cars[-1]['id']]
            cars[-1]['active'] = True

        running = True
        while running:
            self.view.blit(circuit_surface, [0, 0])
            
            for car in cars:
                if not car['active']:
                    continue

                collision = track.collision_car(car['car'])
                car['car'].update_vision(track)

                car['car'].movement = ai.calc_movement(car['id'], car['car'].vision)
                car['car'].apply_movement()

                if(collision == CircuitCircle.COLLISION_WALL):
                    ai.set_evaluation(car['id'], {
                        'perc_of_sectors' : track.get_car_perc_sectors(car['id']),
                        'amount_frames' : track.get_car_num_frames(car['id'], self.view.num_frame)
                    })
                    car['active'] = False
                elif(collision == CircuitCircle.COLLISION_SLOW_AREA):
                    car['car'].set_friction_multiplier(track.slow_friction_multiplier)
                else:
                    car['car'].set_friction_multiplier(1)
                
                if track.finished(car['id']):
                    ai.set_evaluation(car['id'], {
                        'perc_of_sectors' : track.get_car_perc_sectors(car['id']),
                        'amount_frames' : track.get_car_num_frames(car['id'], self.view.num_frame)
                    })
                    car['active'] = False

                if car['active']:
                    car_surface = car['car'].draw()
                    track.update_car_sector(car['id'], car['car'])
                    self.view.blit(car_surface, car['car'].get_pos_surface())

            # self.view.draw_car_ai_eval(cars, ai.features, [0, 0], True)
            self.view.update()

            if ai.population_evaluated():
                if ai.next_generation():
                    for i in range(num_of_cars):
                        cars[i]['name'] = "ai_heur_%.3f" % ai.population[cars[i]['id']]
                        cars[i]['active'] = True
                        self.reset(cars[i]['car'], cars[i]['id'], track)
                else:
                    print("Last generation:")
                    for i in range(num_of_cars):
                        print(ai.population[i], ai.features[i])
                    running = False

            # Events
            for event in pygame.event.get():
                if self.is_exit(event):
                    running = False