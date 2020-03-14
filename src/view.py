import pygame
from car import Car
from collections import deque

class View():
    def __init__(self, config):
        self.width = config['width']
        self.height = config['height']
        self.fps = config['fps']
        self.screen = pygame.display.set_mode((self.width, self.height),
                        pygame.DOUBLEBUF)
        self.font = pygame.font.SysFont('mono', 20, bold=True)
        self.screen.fill((255, 255, 255))
        self.clock = pygame.time.Clock()

        self.sum_of_fps = 0
        self.acum_fps = deque()
        self.acum_fps_window = config['acum_fps_window'] # In number of seconds

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
        self.clock.tick(self.fps)
        self.draw_text(self.width-150, 0, "FPS: %4.1f" % (
                        self.clock.get_fps()), self.font)
        self.acum_fps.append(self.clock.get_fps())
        self.sum_of_fps += self.clock.get_fps()
        if len(self.acum_fps) > self.fps*self.acum_fps_window:
            self.sum_of_fps -= self.acum_fps.popleft()
        self.draw_text(self.width-343, 20, "Avr. FPS (last %ds): %4.1f" % (
                        self.acum_fps_window, self.sum_of_fps/len(self.acum_fps)), 
                        self.font)

        pygame.display.update()
        self.screen.fill((255, 255, 255))            