import pygame
from car import Car
from view import View
from controller import Controller
from circuit_custom import CircuitCustom
from circuit_circle import CircuitCircle
from circuit_ellipse import CircuitEllipse
from ai_manual import AIManual
from ai_ga import AIGA
from datetime import datetime
from functools import partial
import random
import time

class ControllerAI(Controller):
    def __init__(self, config):
        super(Controller, self).__init__()
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
        x_track_offset = self.config['width']//3
        self.start_track()
        self.start_car()
        self.view.num_frame = 0
        self.view.num_frame_now = 0

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
            ai = AIGA(self.config)
        else:
            ai = AIManual(self.config)
        for car in cars:
            car['name'] = "ai_%d" % car['id']

        running = True
        while running:
            self.view.blit(circuit_surface, [x_track_offset, 0])
            
            # Batch check collision for all cars:
            batch_col = self.track.batch_collision_car([car['car'] for car in cars])
            for i in range(num_of_cars):
                cars[i]['collision'] = batch_col[i]

            # Batch check collision for vision in all cars:
            list_shapes = []
            for car in cars:
                list_shapes.extend(car['car'].get_points_vision())
            batch_col = self.track.batch_collision(list_shapes)
            p_now = 0
            for car in cars:
                col_now = batch_col[p_now : p_now + len(car['car'].vision)]
                p_now += len(car['car'].vision)
                car['car'].vision = [col == CircuitCircle.COLLISION_WALL for col in col_now]

            # Set information about first 5 cars on view
            visions = []
            speeds = []
            for car in cars[:1]:
                visions.append(car['car'].vision)
                speeds.append(car['car'].get_speed())
            self.view.set_data_ai_activation(ai.population[:1], visions, speeds)

            for car in cars[1:] + cars[0:1]:
                if not car['active']:
                    continue

                car['car'].movement = ai.calc_movement(car['id'], car['car'].vision, car['car'].get_speed())
                car['car'].apply_movement()

                if(car['collision'] == CircuitCircle.COLLISION_WALL):
                    ai.set_evaluation(car['id'], {
                        'perc_of_sectors' : self.track.get_car_perc_sectors(car['id']),
                        'amount_frames' : self.track.get_car_num_frames(car['id'], self.view.num_frame)
                    })
                    car['active'] = False
                elif(car['collision'] == CircuitCircle.COLLISION_SLOW_AREA):
                    car['car'].set_friction_multiplier(self.track.slow_friction_multiplier)
                else:
                    car['car'].set_friction_multiplier(1)
                
                if self.track.finished(car['id']) or \
                        (car['active'] and \
                            self.track.get_car_num_frames(car['id'], self.view.num_frame) == \
                                self.config['ai']['max_frames']):
                    ai.set_evaluation(car['id'], {
                        'perc_of_sectors' : self.track.get_car_perc_sectors(car['id']),
                        'amount_frames' : self.track.get_car_num_frames(car['id'], self.view.num_frame)
                    })
                    car['active'] = False

                if car['active']:
                    car_surface = car['car'].draw()
                    self.track.update_car_sector(car['id'], car['car'])
                    self.view.blit(car_surface, car['car'].get_pos_surface())

            # self.view.draw_car_ai_eval(cars, ai.features, [0, 60], True)
            self.view.update()

            if ai.population_evaluated():
                if ai.next_generation():
                    self.view.num_frame_now = 0
                    for i in range(num_of_cars):
                        cars[i]['name'] = "ai_%d" % cars[i]['id']
                        cars[i]['active'] = True
                        self.reset(cars[i]['car'], cars[i]['id'], self.track)
                else:
                    running = False

            # Events
            for event in pygame.event.get():
                if self.is_exit(event):
                    running = False