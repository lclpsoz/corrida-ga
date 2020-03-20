from abc import ABCMeta, abstractmethod
import pygame
import time

from circuit.circuit_maker import CircuitMaker
from circuit.circuit_circle import CircuitCircle
from circuit.circuit_ellipse import CircuitEllipse
from circuit.circuit_custom import CircuitCustom

class Controller(metaclass=ABCMeta):
    def __init__(self):
        pass

    def run_circuit_maker(self):
        maker = CircuitMaker(self.config)
         
        running = True
        container = 0
        lst_click = -1
        while running:
            self.view.blit(maker.draw(), [self.config['width']//3,0])

            self.view.draw_text(0, 100, "Garanta que as duas paredes tenham a mesma quantidade de pontos",
                pygame.font.SysFont('mono', 20, bold=True), (255, 0, 0))
            self.view.draw_text(0, 140, "Aperte Espaço quando acabar uma parede",
                pygame.font.SysFont('mono', 20, bold=True), (255, 0, 0))
            self.view.draw_text(0, 180, "Parede1: " + str(len(maker.track_points[0])),
                pygame.font.SysFont('mono', 20, bold=True), (255, 150, 0))
            self.view.draw_text(0, 200, "Parede2: " + str(len(maker.track_points[1])),
                pygame.font.SysFont('mono', 20, bold=True), (255, 150, 0))

            for event in pygame.event.get():
                if self.is_exit(event):
                    return False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    container += maker.finish(container)
                    if container == 2:
                        running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
                    if len(maker.track_points[container]) == 0:
                        container -= 1
                    if container < 0:
                        container = 0
                    else:
                        maker.remove_last_point(container)
                else:
                    mouse = pygame.mouse.get_pressed()
                    if mouse[0] == 1:
                        pos = pygame.mouse.get_pos()
                        if time.time()-lst_click > 0.15 and pos[0] - self.config['width']//3 >= 0:
                            maker.add_point(pos[0] - self.config['width']//3, pos[1], container)
                            lst_click = time.time()

            self.view.update()

        maker.print_points()
        return maker.get_circuit()

    def start_track(self):
        track_name = self.config['track']
        if track_name == "circle":
            self.track = CircuitCircle(self.config)
        elif track_name == "ellipse":
            self.track = CircuitEllipse(self.config)
        elif track_name == "custom":
            self.track = self.run_circuit_maker()
        else:
            self.track = CircuitCustom(self.config, track_name)

    def start_car(self):
        self.config_car = self.config['car']
        self.config_car.update({
            'fps' : self.config['fps'],
            'x' : self.track.start[0],
            'y' : self.track.start[1],
            'start_angle' : self.track.start_angle,
        })