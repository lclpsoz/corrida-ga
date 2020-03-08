import pygame
from dummy_game import dummy_game as game

pygame.init()

game_now = game()
game_now.run()