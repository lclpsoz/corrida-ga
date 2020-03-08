import pygame
from car import car

class dummy_game():
    def __init__(self, width=600, height=600, fps=60):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.fps = fps
        self.font = pygame.font.SysFont('mono', 20, bold=True)

    def draw_text(self, x, y, text, font, color = (255, 0, 255)):
        """Write text in (x, y)
        """
        fw, fh = font.size(text)
        surface = font.render(text, True, color)
        self.screen.blit(surface, (x, y))

    def get_player_data_str(self, player):
        player_data = {}
        player_data['coord'] = str(player.get_pos())
        player_data['speed'] = str("%.2f" % player.get_speed()) + " m/s"
        player_data['dir'] = '(' + str("%.2f" % player.direction[0]) + ', ' + \
                                        str("%.2f" % player.direction[1]) + ')'
        return player_data
        

    def run(self):
        player = car(self.fps, 100, 100)
        car_controls = car.get_controls()
        clock = pygame.time.Clock()

        running = True
        while running:
            self.screen.fill((255, 255, 255))
            player.handle_keys()
            self.screen.blit(player.draw().convert(), player.get_pos())

            # Screen information
            text_pos_top_left = 0
            for control in car_controls:
                self.draw_text(0, text_pos_top_left, control, self.font)
                text_pos_top_left += 20
            player_data = iter(sorted(self.get_player_data_str(player).items()))
            for info in player_data:
                self.draw_text(0, text_pos_top_left,
                    info[0] + " = " + info[1], 
                    pygame.font.SysFont('mono', 15, bold=True))
                text_pos_top_left += 15
            pygame.display.update()

            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        break

            clock.tick(self.fps)
            