from CONST import *
from BUTTON import Button
from ALGO import *
import requests
from bs4 import BeautifulSoup


class App:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((WIN_X, WIN_Y))
        self.running = True
        self.won = False
        self.grid = GRID
        self.font = pygame.font.SysFont("arial", SQUARE_SIZE)
        self.selected = None
        self.mouse_pos = None
        self.show_incorrect = False
        self.solving = False
        self.locked_squares = []
        self.incorrect_squares = []
        self.buttons = []
        self.set_locked_squares()
        pygame.display.set_caption('Sudoku')

    def run(self):
        self.start_load()

        while self.running:
            self.events()
            self.update()
            self.draw()
            time.sleep(1. / 25)

### GAME STATE FUNCTIONS ###
    def draw(self):
        self.window.fill(WHITE)

        self.draw_buttons(self.window)

        if self.selected is not None:
            self.selected_highlights(self.window)
        if self.show_incorrect:
            self.incorrect_highlight(self.window)

        self.draw_grid(self.window)
        self.draw_numbers(self.window)
        pygame.display.update()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                selected = self.mouse_on_grid()
                if selected:
                    self.selected = selected
                else:
                    self.selected = None
                    for button in self.buttons:
                        self.button_handler(button)

            if event.type == pygame.KEYDOWN:
                if self.selected is not None and self.selected not in self.locked_squares:
                    if self.is_int(event.unicode):
                        self.grid[self.selected[1]][self.selected[0]] = int(event.unicode)

    def update(self):
        self.mouse_pos = pygame.mouse.get_pos()

        for button in self.buttons:
            button.update(self.mouse_pos)

        self.update_incorrect()
        if self.grid_filled():
            self.check_win()

### DRAWING FUNCTIONS ###
    def draw_buttons(self, window):
        for button in self.buttons:
            button.draw(window)

    def draw_grid(self, window):
        for i in range(1, BOARD_SIZE):
            pygame.draw.line(window, GREY, (GRID_POS[0], GRID_POS[1] + SQUARE_SIZE * i),
                             (GRID_POS[0] + LINE_LENGTH, GRID_POS[1] + SQUARE_SIZE * i), 2)
            pygame.draw.line(window, GREY, (GRID_POS[0] + SQUARE_SIZE * i, GRID_POS[1]),
                             (GRID_POS[0] + SQUARE_SIZE * i, GRID_POS[1] + LINE_LENGTH), 2)

        for i in range(3, 9, 3):
            pygame.draw.line(window, BLACK, (GRID_POS[0], GRID_POS[1] + SQUARE_SIZE * i),
                             (GRID_POS[0] + LINE_LENGTH, GRID_POS[1] + SQUARE_SIZE * i), 2)
            pygame.draw.line(window, BLACK, (GRID_POS[0] + SQUARE_SIZE * i, GRID_POS[1]),
                             (GRID_POS[0] + SQUARE_SIZE * i, GRID_POS[1] + LINE_LENGTH), 2)

        pygame.draw.lines(window, BLACK, True, [(GRID_POS[0], GRID_POS[1]), (GRID_POS[0], GRID_POS[1] + LINE_LENGTH),
                                                (GRID_POS[0] + LINE_LENGTH, GRID_POS[1] + LINE_LENGTH),
                                                (GRID_POS[0] + LINE_LENGTH, GRID_POS[1])], 3)

    def draw_numbers(self, window):
        for yi, row in enumerate(self.grid):
            for xi, num in enumerate(row):
                color = BLUE
                if num != 0:
                    pos = [xi*SQUARE_SIZE + GRID_POS[0], yi*SQUARE_SIZE + GRID_POS[1]]
                    if (xi, yi) in self.locked_squares:
                        color = BLACK
                    self.text_to_screen(window, str(num), pos, color)

    def highlight_selected(self, window, pos, color):
        pygame.draw.rect(window, color, (pos[0]*SQUARE_SIZE + GRID_POS[0], pos[1]*SQUARE_SIZE + GRID_POS[1],
                                         SQUARE_SIZE, SQUARE_SIZE))

    def highlight_row(self, window, pos):
        for i in range(0, BOARD_SIZE):
            pygame.draw.rect(window, LIGHT_GREY, (i * SQUARE_SIZE + GRID_POS[0], pos[1] * SQUARE_SIZE + GRID_POS[1],
                                                  SQUARE_SIZE, SQUARE_SIZE))

    def highlight_column(self, window, pos):
        for i in range(0, BOARD_SIZE):
            pygame.draw.rect(window, LIGHT_GREY, (pos[0] * SQUARE_SIZE + GRID_POS[0], i * SQUARE_SIZE + GRID_POS[1],
                                                  SQUARE_SIZE, SQUARE_SIZE))

    def highlight_square(self, window, pos):
        square_x = pos[0]//3 * 3
        square_y = pos[1]//3 * 3
        for i in range(3):
            for j in range(3):
                pygame.draw.rect(window, LIGHT_GREY, ((j + square_x) * SQUARE_SIZE + GRID_POS[0],
                                                      (i + square_y) * SQUARE_SIZE + GRID_POS[1], SQUARE_SIZE, SQUARE_SIZE))

    def highlight_same_values(self, window, pos):
        value = self.grid[pos[1]][pos[0]]
        for i, row in enumerate(self.grid):
            for j, val in enumerate(row):
                if val == value and val != 0:
                    self.highlight_selected(window, (j, i), DARK_GREY)

    def incorrect_highlight(self, window):
        for square in self.incorrect_squares:
            if self.grid[square[1]][square[0]] != 0:
                pygame.draw.rect(window, RED, (square[0] * SQUARE_SIZE + GRID_POS[0],
                                               square[1] * SQUARE_SIZE + GRID_POS[1], SQUARE_SIZE, SQUARE_SIZE))

    def selected_highlights(self, window):
        self.highlight_row(window, self.selected)
        self.highlight_column(window, self.selected)
        self.highlight_square(window, self.selected)
        self.highlight_same_values(window, self.selected)
        self.highlight_selected(window, self.selected, YELLOW)

### CHECKING FUNCTIONS ###
    def check_win(self):
        if len(self.incorrect_squares) == 0:
            self.won = True

    def update_incorrect(self):
        self.incorrect_squares = []
        self.check_rows()
        self.check_cols()
        self.check_squares()

    def check_rows(self):
        for yi, row in enumerate(self.grid):
            possible = [1, 2, 3, 4, 5, 6, 7, 8, 9]
            for xi in range(9):
                if self.grid[yi][xi] in possible:
                    possible.remove(self.grid[yi][xi])
                else:
                    if (xi, yi) not in self.incorrect_squares and (xi, yi) not in self.incorrect_squares:
                        self.incorrect_squares.append((xi, yi))
                    if (xi, yi) in self.locked_squares:
                        for i in range(9):
                            if self.grid[yi][i] == self.grid[yi][xi] and [i, yi] not in self.locked_squares:
                                self.incorrect_squares.append([i, yi])

    def check_cols(self):
        for xi in range(9):
            possible = [1, 2, 3, 4, 5, 6, 7, 8, 9]
            for yi in range(9):
                if self.grid[yi][xi] in possible:
                    possible.remove(self.grid[yi][xi])
                else:
                    if (xi, yi) not in self.incorrect_squares and (xi, yi) not in self.incorrect_squares:
                        self.incorrect_squares.append((xi, yi))
                    if (xi, yi) in self.locked_squares:
                        for j in range(9):
                            if self.grid[j][xi] == self.grid[yi][xi] and (xi, j) not in self.locked_squares:
                                self.incorrect_squares.append((xi, j))

    def check_squares(self):
        for x in range(3):
            for y in range(3):
                possible = [1, 2, 3, 4, 5, 6, 7, 8, 9]
                for i in range(3):
                    for j in range(3):
                        xi = x*3+i
                        yi = y*3+j
                        if self.grid[yi][xi] in possible:
                            possible.remove(self.grid[yi][xi])
                        else:
                            if (xi, yi) not in self.incorrect_squares and (xi, yi) not in self.locked_squares:
                                self.incorrect_squares.append((xi, yi))
                            if (xi, yi) in self.locked_squares:
                                for i in range(3):
                                    for j in range(3):
                                        xi2 = x*3+i
                                        yi2 = y*3+j
                                        if self.grid[yi2][xi2] == self.grid[yi][xi] and (xi2, yi2) not in self.locked_squares:
                                            self.incorrect_squares.append((xi2, yi2))

### HELPER FUNCTIONS ###
    def text_to_screen(self, window, text, pos, color):
        font = self.font.render(text, False, color)
        font_width = font.get_width()
        font_height = font.get_height()
        pos[0] += (SQUARE_SIZE - font_width)/2
        pos[1] += (SQUARE_SIZE - font_height)/2
        window.blit(font, pos)

    def mouse_on_grid(self):
        if self.mouse_pos[0] < GRID_POS[0] or self.mouse_pos[1] < GRID_POS[1]:
            return False
        elif self.mouse_pos[0] > GRID_POS[0]+LINE_LENGTH or self.mouse_pos[1] > GRID_POS[1]+LINE_LENGTH:
            return False
        return (self.mouse_pos[0] - GRID_POS[0])//SQUARE_SIZE, (self.mouse_pos[1] - GRID_POS[1])//SQUARE_SIZE

    def set_locked_squares(self):
        for yi, row in enumerate(self.grid):
            for xi, num in enumerate(row):
                if num != 0:
                    self.locked_squares.append((xi, yi))

    def is_int(self, string):
        try:
            int(string)
            return True
        except:
            return False

    def grid_filled(self):
        for row in self.grid:
            for num in row:
                if num == 0:
                    return False

        return True

    def revert_grid(self):
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                if (x, y) not in self.locked_squares:
                    self.grid[y][x] = 0

    def switch_visibility(self):
        self.show_incorrect = not self.show_incorrect

    def load_buttons(self):
        self.buttons = []
        self.buttons.append(Button(EDGE_X, 2*EDGE_Y + LINE_LENGTH, 40, 120, "Show Incorrect", function=self.switch_visibility))
        self.buttons.append(Button(EDGE_X + 160, 2*EDGE_Y + LINE_LENGTH, 40, 80, "Solve", "Algo", function=backtrack_solve))
        self.buttons.append(Button(EDGE_X + 280, 2*EDGE_Y + LINE_LENGTH, 40, 120, "Fast Solve", "Algo", function=backtrack_solve))


        self.buttons.append(Button(EDGE_X + LINE_LENGTH + 40, 3*EDGE_Y + 60, 40, 80, "Easy", function=self.get_puzzle, params="1"))
        self.buttons.append(Button(EDGE_X + LINE_LENGTH + 40, 3*EDGE_Y + 2*60, 40, 80, "Medium", function=self.get_puzzle, params="2"))
        self.buttons.append(Button(EDGE_X + LINE_LENGTH + 40, 3*EDGE_Y + 3*60, 40, 80, "Hard", function=self.get_puzzle, params="3"))
        self.buttons.append(Button(EDGE_X + LINE_LENGTH + 40, 3*EDGE_Y + 4*60, 40, 80, "Evil", function=self.get_puzzle, params="4"))

    def button_handler(self, button):
        if button.highlighted:
            button.highlighted = False
            if button.type == "Algo":
                self.show_incorrect = False
                self.solving = True
                self.revert_grid()

                instant = False
                if button.text == "Fast Solve":
                    instant = True
                button.update_params((lambda: self.draw(), self.grid, instant))
            button.click()

    def get_puzzle(self, difficulty):
        # difficulty from 1 to 4
        html = requests.get("https://nine.websudoku.com/?level={}".format(difficulty)).content
        soup = BeautifulSoup(html, features="html.parser")
        ids = self.create_ids()
        data = []
        for idd in ids:
            data.append(soup.find('input', id=idd))

        board = [[0 for i in range(9)] for i in range(9)]
        for i, square in enumerate(data):
            try:
                board[i//9][i%9] = int(square['value'])
            except:
                pass
        self.grid = board
        self.start_load()

    def create_ids(self):
        ids = []
        for i in range(9):
            for j in range(9):
                ids.append("f{}{}".format(j, i))

        return ids

    def start_load(self):
        self.buttons = []
        self.load_buttons()
        self.locked_squares = []
        self.incorrect_squares = []
        self.won = False
        self.set_locked_squares()
