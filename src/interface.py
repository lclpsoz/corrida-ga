import pygame
import pygame_gui
import json
import random

from view import View
from controller.controller_player import ControllerPlayer
from controller.controller_ai import ControllerAI

def run():
    pygame.init()
    config = dict(json.load(open('src/config.json')))

    if 'seed' in config:
        random.seed(config['seed'])
    else:
        seed = random.randint(0, int(2**64-1))
        print("seed =", seed)
        random.seed(seed)

    pygame.display.set_caption('F1 with GA')
    window_surface = pygame.display.set_mode((1200, 600))
    view = View(config)
    view.screen = window_surface

    background = pygame.Surface((1200, 600))
    background.fill((255, 255, 255))

    manager = pygame_gui.UIManager((1200, 600))

    btn_ga = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((50, 200), (200, 50)),
        text='Algoritmo Genético',
        manager=manager
    )
    btn_player = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((50, 250), (200, 50)),
        text='Direção Manual',
        manager=manager
    )
    btn_ai_manual = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((50, 300), (200, 50)),
        text='I.A. Arbitrária',
        manager=manager
    )
    btn_exit = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((50, 350), (200, 50)),
        text='Sair',
        manager=manager
    )

    # entry_text = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((350, 475), (100, 50)),
    #                                             manager=manager)

    clock = pygame.time.Clock()
    running = True

    while running:
        time_delta = clock.tick(60)/1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.USEREVENT:
                if event.user_type == 'ui_button_pressed':
                    if event.ui_element == btn_player:
                        ControllerPlayer(config).run()
                    elif event.ui_element == btn_ga:
                        ControllerAI(config).run()
                    elif event.ui_element == btn_exit:
                        running = False
                elif event.user_type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                    print("Here:", event.text)

            manager.process_events(event)

        manager.update(time_delta)

        view.blit(background, (0, 0))
        view.draw_text(220, 20,
                        "Carro autônomo em pista 2D",
                        pygame.font.SysFont('arial', 60, bold=False),
                        (0, 0, 0))
        manager.draw_ui(view.screen)

        pygame.display.update()
