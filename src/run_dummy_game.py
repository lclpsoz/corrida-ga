import pygame
from dummy_game import dummy_game as game

pygame.init()

game_now = game(1200, 600, 60)
game_now.run()