import pygame
from controller import controller
from view import view
from car import car

pygame.init()

config = {  'width' : 1200,
            'height': 600,
            'fps' : 60      }

game_now = controller(config)
game_now.run()

pygame.quit()