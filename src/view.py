import pygame
from car import Car

class View():
    def __init__(self, config):
        self.width = config['width']
        self.height = config['height']
        self.fps = config['fps']
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.font = pygame.font.SysFont('mono', 20, bold=True)
        self.screen.fill((255, 255, 255))

    def draw_text(self, x, y, text, font, color = (255, 0, 255)):
        """Write text in (x, y)"""
        fw, fh = font.size(text)
        surface = font.render(text, True, color)
        self.blit(surface, (x, y))

    def blit(self, surface, pos):
        """Draw surface on screen."""
        self.screen.blit(surface, pos)

    def draw_player_data(self, player_data, pos):
        """Write input player_data to screen, starting on pos."""
        player_data = iter(sorted(player_data.items()))
        for info in player_data:
            self.draw_text(pos[0], pos[1],
                info[0] + " = " + info[1], 
                pygame.font.SysFont('mono', 15, bold=True))
            pos[1] += 15

    def draw_car_controls(self, car_controls, pos):
        """Write input car_controls to screen, starting on pos."""
        for control in car_controls:
            self.draw_text(pos[0], pos[1], control, self.font)
            pos[1] += 20

    def update(self):
        """Updates frame."""
        clock = pygame.time.Clock()
        pygame.display.update()
        clock.tick(self.fps)
        self.screen.fill((255, 255, 255))            