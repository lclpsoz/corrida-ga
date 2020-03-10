import pygame
from controller import Controller
from view import View

pygame.init()

config = {  'width' : 1200,
            'height': 600,
            'fps' : 60      }

game_now = Controller(config)
game_now.run()

pygame.quit()