import pygame
from car import car

class dummy_game():
    def __init__(self, width=600, height=600, fps=30):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.fps = fps
        self.font = pygame.font.SysFont('mono', 20, bold=True)

    def draw_text(self, x, y, text, color = (255, 0, 255)):
        """Write text in (x, y)
        """
        fw, fh = self.font.size(text)
        surface = self.font.render(text, True, color)
        self.screen.blit(surface, (x, y))

    def run(self):
        player = car()
        car_controls = car.get_controls()
        clock = pygame.time.Clock()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            self.screen.fill((255, 255, 255))
            player.handle_keys()
            self.screen.blit(player.draw().convert(), player.get_pos())
            for i in range(len(car_controls)):
                self.draw_text(0, 20*i, car_controls[i])
            pygame.display.update()

            clock.tick(self.fps)
            