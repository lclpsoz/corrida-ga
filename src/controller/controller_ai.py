import pygame
import random
import time
from datetime import datetime
from functools import partial
from collections import deque
from pprint import pprint

from car import Car
from view import View
from controller.controller import Controller
from circuit.circuit import Circuit
from ai.ai_manual import AIManual
from ai.ai_ga import AIGA

class ControllerAI(Controller):
    def __init__(self, config, ai_info = None):
        super(Controller, self).__init__()
        self.view = View(config)
        self.config = config
        self.ai_info = ai_info
        pprint(config)

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

    def deactivate_car(self, car, ai):
        """Deactivate a car and set evaluation to ai."""
        ai.set_evaluation(car['id'], {
            'perc_of_sectors' : self.track.get_car_perc_sectors(car['id']),
            'amount_frames' : self.track.get_car_num_frames(car['id'], self.view.num_frame)
        })
        car['active'] = False

    def run(self):
        """Run project."""
        x_track_offset = self.config['width']//3
        self.start_track()
        if self.track == None:
            return
        self.start_car()
        self.view.num_frame = 0
        self.view.num_frame_now = 0

        if self.config["graphics"]:
            circuit_surface = self.track.draw()

        num_of_cars = self.config['ai']['population_size']        
        cars = []
        colors = [list(x[1]) for x in pygame.color.THECOLORS.items()]
        to_remove = []
        for x in colors:
            if sum(x[:3]) < 255//2 or sum(x[:3]) > 255*2 or max(x[:3]) == 255 or min(x[:3]) <= 30:
                to_remove.append(x)
        for x in to_remove:
            colors.remove(x)
        colors = [(x[0], x[1], x[2], 80) for x in colors]
        if num_of_cars >= len(colors):
            cars_colors = random.choices(colors, k=(num_of_cars-1))
        else:
            cars_colors = random.sample(colors, k=(num_of_cars-1))
        while(len(cars) < num_of_cars):
            config_car_now = self.config_car.copy()
            if len(cars) == 0:
                config_car_now['car_color'] = (0, 0, 255, 255)
            else:
                config_car_now['car_color'] = cars_colors.pop()
                config_car_now['front_color'][3] = 80
            cars.append({})
            cars[-1]['car'] = Car(config_car_now)
            cars[-1]['id'] = self.track.add_car(cars[-1], self.view.num_frame)
            cars[-1]['active'] = True
            if len(cars) == 1:
                cars[-1]['car'].show_vision = True

        if self.config['ai']['type'] == 'ga':
            ai = AIGA(self.config, self.ai_info)
        else:
            ai = AIManual(self.config)
        for car in cars:
            car['name'] = "ai_%d" % car['id']

        # To check if all cars are doing something, a list of deques with the
        # last x delta_pixels of each car.
        history_length = 3
        delta_pixels_hist = [deque([1 for x in range(history_length)]).copy() for x in range(num_of_cars)]

        running = True
        while running:
            if self.config["graphics"]:
                self.view.blit(circuit_surface, [x_track_offset, 0])
            
            # Batch check collision for all cars:
            batch_col = self.track.batch_collision_car([car['car'] for car in cars])
            for i in range(num_of_cars):
                cars[i]['collision'] = batch_col[i]

            # Batch update vision in all cars:
            list_shapes = []
            for car in cars:
                list_shapes.extend(car['car'].get_points_vision())
            batch_col = self.track.batch_collision_dist(list_shapes)
            p_now = 0
            for car in cars:
                dists_col = batch_col[p_now : p_now + len(car['car'].vision)]
                p_now += len(car['car'].vision)
                car['car'].vision = [x/car['car'].vision_length for x in dists_col]

            # Set information about first car on view
            visions = []
            speeds = []
            for car in cars[:1]:
                visions.append(car['car'].vision)
                speeds.append(car['car'].get_speed())
            self.view.set_data_ai_activation(ai.population[:1], visions, speeds)

            # First car (cars[0:1]) is updated last, to be on top of all others
            for car in cars[1:] + cars[0:1]:
                if not car['active']:
                    continue
                # Draw Car
                if self.config["graphics"]:
                    car_surface = car['car'].draw()
                    if self.config["graphics"]:
                        self.view.blit(car_surface, car['car'].get_pos_surface())
                # Update car sector
                self.track.update_car_sector(car['id'], car['car'])
                # Update delta_pixels history:
                delta_pixels_hist[car['id']].popleft()
                delta_pixels_hist[car['id']].append(car['car'].delta_pixels)

                car['car'].movement = ai.calc_movement(car['id'], car['car'].vision, car['car'].get_speed())
                car['car'].apply_movement()

                if(car['collision'] == Circuit.COLLISION_WALL):
                    self.deactivate_car(car, ai)
                else:
                    car['car'].set_friction_multiplier(1)
                
                if self.track.finished(car['id']) or \
                        (car['active'] and \
                            self.track.get_car_num_frames(car['id'], self.view.num_frame) == \
                                ai.max_frames):
                    self.deactivate_car(car, ai)

                if self.view.num_frame_now > 15 and car['active'] and sum(delta_pixels_hist[car['id']]) < 0.5:
                    self.deactivate_car(car, ai)
                    

            # self.view.draw_car_ai_eval(cars, ai.features, [0, 60], True)
            self.view.update()

            # Generation is over
            if ai.population_evaluated():
                if ai.next_generation():
                    self.view.num_frame_now = 0
                    for i in range(num_of_cars):
                        cars[i]['name'] = "ai_%d" % cars[i]['id']
                        cars[i]['active'] = True
                        self.reset(cars[i]['car'], cars[i]['id'], self.track)
                    delta_pixels_hist = [deque([1 for x in range(history_length)]).copy() for x in range(num_of_cars)]
                else:
                    running = False

            # Events
            for event in pygame.event.get():
                if self.is_exit(event):
                    running = False