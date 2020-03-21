import pygame
import pygame_gui
import json
import random

from view import View
from controller.controller_player import ControllerPlayer
from controller.controller_ai import ControllerAI

class Interface():
    def __init__(self):
        pygame.init()
        self.config = dict(json.load(open('src/config.json')))
        if 'seed' in self.config:
            random.seed(self.config['seed'])
        else:
            seed = random.randint(0, int(2**64-1))
            print("seed =", seed)
            random.seed(seed)

        pygame.display.set_caption('F1 with GA')
        self.view = View(self.config)

        self.background = pygame.Surface((1200, 600))
        self.background.fill(pygame.Color("#ffffff"))

        self.manager = pygame_gui.UIManager((1200, 600), 'src/theme.json')
        
        self.menu_btns(50, 200)
        self.all_configs = json.load(open("src/all-configs.json"))
        self.all_fields = []
        self.menu_config(300, 100, self.all_configs)

    def menu_btns(self, x : int, y : int):
        """Create menu buttons. Receive top left position of principal menu buttons."""
        x_delta = 0
        y_delta = 50
        elem_size = (200, 50)
        self.btn_ga = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((x, y), elem_size),
            text='Algoritmo Genético',
            manager=self.manager
        )
        x += x_delta
        y += y_delta
        self.btn_player = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((x, y), elem_size),
            text='Direção Manual',
            manager=self.manager
        )
        x += x_delta
        y += y_delta
        self.btn_ai_manual = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((x, y), elem_size),
            text='I.A. Arbitrária',
            manager=self.manager
        )
        x += x_delta
        y += y_delta
        self.btn_exit = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((x, y), elem_size),
            text='Sair',
            manager=self.manager
        )

    def menu_config(self, x : int, y : int, all_configs : dict):
        """Interface for personalization of config."""
        elem_size = (200, 50)
        all_x = []
        for v in range(x, self.config['width']-elem_size[0]*2 + 1, elem_size[0]*2):
            all_x.append(v)
        all_y = []
        for v in range(y, self.config['height']-elem_size[1] + 1, elem_size[1]):
            all_y.append(v)
        
        # Alert to press Enter
        pygame_gui.elements.ui_label.UILabel(
            relative_rect=pygame.Rect((all_x[-1], all_y[-1]), (elem_size[0]*2, elem_size[1])),
            manager=self.manager,
            text="Press ENTER to set values!"
        )

        float_chars = ['0','1','2','3','4','5','6','7','8','9','.']
        categories = ["geral", "ai"]
        for i in range(len(categories)):
            category = categories[i]
            # Title of column
            pygame_gui.elements.ui_label.UILabel(
                relative_rect=pygame.Rect((all_x[i], all_y[0]), (elem_size[0]*2, elem_size[1])),
                manager=self.manager,
                text=category.upper()
            )

            items = list(all_configs[category].keys())
            fields = sorted([(x, all_configs[category][x]) for x in items])[::-1]
            for j in range(1, len(fields)+1):
                field = fields[j-1]
                # Label
                pygame_gui.elements.ui_label.UILabel(
                    relative_rect=pygame.Rect((all_x[i], all_y[j]), elem_size),
                    manager=self.manager,
                    text=field[0] + ":",
                )
                if isinstance(field[1], str):
                    # User input
                    entry_text = pygame_gui.elements.UITextEntryLine(
                        relative_rect=pygame.Rect((all_x[i]+elem_size[0], all_y[j]+10), elem_size),
                        manager=self.manager,
                        object_id=field[0]
                    )
                    self.all_fields.append(entry_text)
                    if "FLOAT" in field[1]:
                        entry_text.set_allowed_characters(allowed_characters=float_chars)
                    else:
                        entry_text.set_allowed_characters('numbers')

                    if category == 'ai':
                        if field[0] == "max_frames":
                            pass
                        else:
                            entry_text.set_text(str(self.config['ai'][field[0]]))
                    elif field[0] == 'car_visions':
                        entry_text.set_text(str(self.config['car']['number_of_visions']))
                    elif field[0] == 'car_vision_len':
                        entry_text.set_text(str(self.config['car']['vision_length']))
                    else:
                        entry_text.set_text(str(self.config[field[0]]))

                else:
                    # Drop down menu
                    pygame_gui.elements.UIDropDownMenu(
                        options_list=list([str(x) for x in field[1]]),
                        relative_rect=pygame.Rect((all_x[i]+elem_size[0], all_y[j]), elem_size),
                        manager=self.manager,
                        starting_option=str(list(field[1])[0]),
                        object_id=field[0]
                    )

    def set_config(self, field, text):
        """Receive field and text to be setted on config dict."""
        if field in self.all_configs['ai']:
            if self.all_configs['ai'][field].endswith('FLOAT'):
                tp = float
            else:
                tp = int
        elif not field.startswith("car"):
            if self.all_configs['geral'][field].endswith('FLOAT'):
                tp = float
            else:
                tp = int

        if field in self.config['ai'] or field == 'max_frames':
            try:
                self.config['ai'][field] = tp(text)
            except:
                print(text, "is a invalid input in", field)
        elif field == 'car_visions':
            try:
                self.config['car']['number_of_visions'] = int(text)
            except:
                print(text, "is a invalid input in", field)
        elif field == 'car_vision_len':
            try:
                self.config['car']['vision_length'] = int(text)
            except:
                print(text, "is a invalid input in", field)
        else:
            try:
                self.config[field] = tp(text)
            except:
                print(text, "is a invalid input in", field)


    def set_interface_config(self):
        """Read all fields in the interface and set them in the config dict."""
        for ui_elem in self.all_fields:
            if ui_elem.text != '':
                self.set_config(ui_elem.object_ids[0], ui_elem.text)

    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            time_delta = clock.tick(60)/1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.USEREVENT:
                    if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                        self.set_interface_config()
                        if event.ui_element == self.btn_player:
                            ControllerPlayer(self.config).run()
                        elif event.ui_element == self.btn_ga:
                            ControllerAI(self.config).run()
                        elif event.ui_element == self.btn_exit:
                            running = False
                    elif event.user_type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                        self.set_config(event.ui_object_id, event.text)
                    elif event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                        if event.ui_object_id == "verbose":
                            self.config[event.ui_object_id] = int(event.text)
                        else:
                            self.config[event.ui_object_id] = event.text

                self.manager.process_events(event)

            self.manager.update(time_delta)

            self.view.blit(self.background, (0, 0))
            self.view.draw_text(220, 20,
                            "Carro autônomo em pista 2D",
                            pygame.font.SysFont('arial', 60, bold=False),
                            pygame.Color("#000000"))
            self.manager.draw_ui(self.view.screen)

            pygame.display.update()
