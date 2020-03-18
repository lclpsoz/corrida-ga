import pygame
from car import Car
from view import View
from circuit_circle import CircuitCircle
from circuit_ellipse import CircuitEllipse
from ai_manual import AIManual
from ai_ga import AIGA
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
        x_track_offset = self.config['width']//3
        if self.config['track'] == 'circle':
            track = CircuitCircle(self.config)
        else:
            track = CircuitEllipse(self.config)
        circuit_surface = track.draw()

        config_car = self.config['car']
        config_car.update({
            'fps' : self.config['fps'],
            'x' : track.start[0],
            'y' : track.start[1],
            'start_angle' : track.start_angle,
        })

        num_of_cars = self.config['ai']['population_size']        
        cars = []
        cars_colors = random.sample(pygame.color.THECOLORS.items(), k=num_of_cars)
        while(len(cars) < num_of_cars):
            config_car_now = config_car.copy()
            config_car_now['car_color'] = cars_colors.pop()[1]
            cars.append({})
            cars[-1]['car'] = Car(config_car_now)
            cars[-1]['id'] = track.add_car(cars[-1], self.view.num_frame)
            cars[-1]['active'] = True

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
            batch_col = track.batch_collision_car([car['car'] for car in cars])
            for i in range(num_of_cars):
                cars[i]['collision'] = batch_col[i]

            # Batch check collision for vision in all cars:
            list_shapes = []
            for car in cars:
                list_shapes.extend(car['car'].get_points_vision())
            batch_col = track.batch_collision(list_shapes)
            p_now = 0
            for car in cars:
                col_now = batch_col[p_now : p_now + len(car['car'].vision)]
                p_now += len(car['car'].vision)
                car['car'].vision = [col == CircuitCircle.COLLISION_WALL for col in col_now]

            for car in cars:
                if not car['active']:
                    continue

                car['car'].movement = ai.calc_movement(car['id'], car['car'].vision, car['car'].get_speed())
                car['car'].apply_movement()

                if(car['collision'] == CircuitCircle.COLLISION_WALL):
                    ai.set_evaluation(car['id'], {
                        'perc_of_sectors' : track.get_car_perc_sectors(car['id']),
                        'amount_frames' : track.get_car_num_frames(car['id'], self.view.num_frame)
                    })
                    car['active'] = False
                elif(car['collision'] == CircuitCircle.COLLISION_SLOW_AREA):
                    car['car'].set_friction_multiplier(track.slow_friction_multiplier)
                else:
                    car['car'].set_friction_multiplier(1)
                
                if track.finished(car['id']) or \
                        (car['active'] and \
                            track.get_car_num_frames(car['id'], self.view.num_frame) == \
                                self.config['ai']['max_frames']):
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
                    self.view.num_frame_now = 0
                    for i in range(num_of_cars):
                        cars[i]['name'] = "ai_%d" % cars[i]['id']
                        cars[i]['active'] = True
                        self.reset(cars[i]['car'], cars[i]['id'], track)
                else:
                    running = False

            # Events
            for event in pygame.event.get():
                if self.is_exit(event):
                    running = False