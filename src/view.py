import pygame
from collections import deque

from car import Car

class View():
    def __init__(self, config):
        self.config = config
        self.EPS = config['EPS']
        self.width = config['width']
        self.height = config['height']
        self.fps = config['fps']
        self.fps_info = config['fps_info']
        self.screen = pygame.display.set_mode((self.width, self.height),
                        pygame.DOUBLEBUF)
        self.font = pygame.font.SysFont('mono', 20, bold=False)
        self.screen.fill((0, 0, 0))
        pygame.display.update()
        self.clock = pygame.time.Clock()

        self.num_frame = 0
        self.num_frame_now = 0

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

    def draw_car_ai_eval(self, cars, features, pos : list, sort = False):
        """Write information about cars evaluation starting in pos."""
        cars_evals = []
        for feat in features:
            if feat:
                cars_evals.append((feat['perc_of_sectors'], feat['amount_frames']))
            else:
                cars_evals.append(None)
        prt = [(cars[i]['name'], cars_evals[i]) for i in range(len(cars))]
        if sort:
            prt.sort(key=lambda x : (-x[1][0], x[1][1]) if x[1] else (1e18, 1e18))

        font_size = 15
        for p in prt:
            if p[1]:
                txt = p[0] + " : " + ("p=%.2f, f=%d" % tuple(p[1]))
            else:
                txt = p[0] + " = None"
            self.draw_text(pos[0], pos[1],
                txt, 
                pygame.font.SysFont('mono', font_size, bold=False))
            pos[1] += font_size+4
            if pos[1] > self.height:
                return

    def set_data_ai_activation(self, population : list, visions : list, speeds : float):
        """Receive list of individuals, vision and speed. Organize the data
        to be presentend on screen."""
        self.population = population
        self.visions = visions
        self.speeds = speeds

    def draw_ai_activation(self, pos):
        """Draw representation for activation in AIs that was previously
        setted as attribute."""
        def get_color(x):
            ret = (0,0,0)
            if x > self.EPS:
                ret = (0, 254, 0)
            elif x < -self.EPS:
                ret = (255, 0, 0)
            return ret
        font_size = 18
        font = pygame.font.SysFont('mono', font_size, bold=True)
        surface = pygame.Surface((400, 600))
        surface.set_colorkey((0, 255, 0))
        surface.fill((0, 255, 0))
        for i in range(len(self.population)):
            self.draw_text(pos[0], pos[1], "%s%s" % (" "*13, "car_" + str(i+1)), font)
            pos[1] += font_size
            self.draw_text(pos[0], pos[1], "  ACC  | BREAK | LEFT  | RIGHT |",
                            font, (0, 0, 0))
            pos[1] += font_size
            indv = self.population[i]
            vision = self.visions[i]
            speed = self.speeds[i]
            for j in range(len(indv)):
                total = 0
                ori_pos_1 = pos[1]
                pygame.draw.line(surface, (0, 0, 0), [82+pos[0], pos[1]],
                                                        [82+pos[0], pos[1]+500])
                for k in range(len(indv[j])-1):
                    total += vision[k]*indv[j][k+1]
                    if vision[k]:
                        color = (255, 0, 0)
                    else:
                        color = (0, 254, 0)
                    self.draw_text(pos[0], pos[1], str("%.1f" % vision[k]), font, color)
                    self.draw_text(pos[0]+font_size-1, pos[1], "*", font, (0,0,0))
                    self.draw_text(pos[0]+(font_size-1)*2-1, pos[1],
                                        "%+1.1f" % indv[j][k+1],
                                        font, get_color(indv[j][k+1]))
                    pos[1] += font_size
                self.draw_text(pos[0], pos[1], "S=%+05.1f" % total, font, get_color(total))
                pos[1] += font_size
                self.draw_text(pos[0], pos[1], "_______", font, (0,0,0))
                pos[1] += font_size
                self.draw_text(pos[0], pos[1], "V= %04.1f" % speed, font, (0,0,0))
                pos[1] += font_size
                self.draw_text(pos[0], pos[1], "*", font, (0,0,0))
                self.draw_text(pos[0]+2*font_size-2, pos[1], "%+04.1f" % indv[j][0], font, get_color(indv[j][0]))
                pos[1] += font_size
                self.draw_text(pos[0], pos[1], "=======", font, (0,0,0))
                pos[1] += font_size
                self.draw_text(pos[0], pos[1], "  %+05.1f" % (speed*indv[j][0]), font, get_color(speed*indv[j][0]))
                total += speed*indv[j][0]
                pos[1] += font_size
                self.draw_text(pos[0], pos[1], "_______", font, (0,0,0))
                pos[1] += font_size
                self.draw_text(pos[0], pos[1], "S=%+05.1f" % (total), font, get_color(total))
                pos[1] += font_size

                if total > self.EPS:
                    self.draw_text(pos[0], pos[1], " ACTIV ", font, (0,254,0))
                else:
                    self.draw_text(pos[0], pos[1], "DEACTIV", font, (255,0,0))
                pos[1] = ori_pos_1
                pos[0] += int(font_size * 5)-2
            pos[1] += font_size
        self.blit(surface, [0, 0])


    def update(self):
        """Updates frame."""
        self.clock.tick(self.fps)
        self.acum_fps.append(self.clock.get_fps())
        self.sum_of_fps += self.clock.get_fps()
        if len(self.acum_fps) > self.fps*self.acum_fps_window:
            self.sum_of_fps -= self.acum_fps.popleft()

        if self.num_frame%(self.fps//self.fps_info) == 0:
            self.draw_text(0, 0, "FPS: %4.1f" % (
                            self.clock.get_fps()), self.font)
            self.draw_text(0, 20, "Avr. FPS (last %ds): %4.1f" % (
                            self.acum_fps_window, self.sum_of_fps/len(self.acum_fps)), 
                            self.font)
            self.draw_text(0, 40, "Num of frames: %4d|%8d" % (self.num_frame_now, self.num_frame), 
                            self.font)
            if hasattr(self, 'population'):
                self.draw_ai_activation([0, 60])
            pygame.display.update(pygame.Rect((0, 0), (self.width//3 - 1, self.height)))
        if self.config["graphics"]:
            pygame.display.update(pygame.Rect((self.width//3, 0), (2*self.width//3, self.height)))
        self.num_frame += 1
        self.num_frame_now += 1
        # if self.num_frame%60 == 0:
        #     print("Avr. FPS (last %ds): %4.1f" % (\
        #                 self.acum_fps_window, self.sum_of_fps/len(self.acum_fps)))
        self.screen.fill((255, 255, 255))