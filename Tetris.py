import pygame, sys

pygame.init()
pygame.font.init()
import random
from pygame.locals import *
from pygame import mixer

mixer.init()


# Color list
class Colors:
    grey = (26, 31, 40)
    green = (47, 230, 23)
    red = (232, 18, 18)
    orange = (226, 116, 17)
    yellow = (237, 234, 4)
    purple = (166, 0, 247)
    cyan = (21, 204, 209)
    blue = (13, 134, 216)
    white = (255, 255, 255)
    dark_blue = (44, 44, 127)
    light_blue = (59, 85, 162)

    @classmethod
    def get_cell_colors(cls):
        return [
            cls.grey,
            cls.green,
            cls.red,
            cls.orange,
            cls.yellow,
            cls.purple,
            cls.cyan,
            cls.blue,
        ]


# Creating a network of the game
class Grid:
    def __init__(self):
        self.num_rows = 20
        self.num_cols = 10
        self.cell_size = 30
        self.grid = [[0 for j in range(self.num_cols)] for i in range(self.num_rows)]
        self.colors = Colors.get_cell_colors()

    # Browsing the playing surface
    def is_inside(self, row, colum):
        if row >= 0 and row < self.num_rows and colum >= 0 and colum < self.num_cols:
            return True
        return False

    def is_empty(self, row, colum):
        if self.grid[row][colum] == 0:
            return True
        return False

    def is_row_full(self, row):
        for colum in range(self.num_cols):
            if self.grid[row][colum] == 0:
                return False
        return True

    def clear_row(self, row):
        for colum in range(self.num_cols):
            self.grid[row][colum] = 0

    def move_row_down(self, row, num_rows):
        for colum in range(self.num_cols):
            self.grid[row + num_rows][colum] = self.grid[row][colum]
            self.grid[row][colum] = 0

    def clear_full_rows(self):
        completed = 0
        for row in range(self.num_rows - 1, 0, -1):
            if self.is_row_full(row):
                self.clear_row(row)
                completed += 1
            elif completed > 0:
                self.move_row_down(row, completed)
        return completed

    def reset(self):
        for row in range(self.num_rows):
            for colum in range(self.num_cols):
                self.grid[row][colum] = 0

    # A function to apply the colors on the game board
    def draw(self, screen):
        for row in range(self.num_rows):
            for colum in range(self.num_cols):
                cell_value = self.grid[row][colum]
                cell_rect = pygame.Rect(
                    colum * self.cell_size + 11,
                    row * self.cell_size + 11,
                    self.cell_size - 1,
                    self.cell_size - 1,
                )
                pygame.draw.rect(
                    screen, self.colors[cell_value], cell_rect, border_radius=3
                )


class Game:
    def __init__(self):
        self.grid = Grid()
        self.blocks = [
            L1Block(),
            L2Block(),
            Z1Block(),
            Z2Block(),
            TBlock(),
            OBlock(),
            IBlock(),
        ]
        self.current_block = self.get_random_block()
        self.next_block = self.get_random_block()
        self.game_over = False
        self.score = 0
        self.paused = False
        self.runing_game = 400
        self.data = 0
        self.record_change = False
        mixer.music.load("TetrisRemix.mp3")
        pygame.mixer.music.play(-1)

    def run(self):
        if self.score >= 1000 and self.runing_game == 400:
            self.runing_game = 300
            return False
        elif self.score >= 2000 and self.runing_game == 300:
            self.runing_game = 250
            return False
        elif self.score >= 3000 and self.runing_game == 250:
            self.runing_game = 150
        elif self.score >= 4000 and self.runing_game == 150:
            self.runing_game = 120
            return False
        return True

        # movement speed

    def update_score(self, lines_cleared, move_down_points):
        if lines_cleared == 1:
            self.score += 100
        elif lines_cleared == 2:
            self.score += 300
        elif lines_cleared == 3:
            self.score += 500
        elif lines_cleared == 4:
            self.score += 700
        self.score += move_down_points

    def get_random_block(self):
        if len(self.blocks) == 0:
            self.blocks = [
                L1Block(),
                L2Block(),
                Z1Block(),
                Z2Block(),
                TBlock(),
                OBlock(),
                IBlock(),
            ]
        block = random.choice(self.blocks)
        self.blocks.remove(block)
        return block

    def move_right(self):
        self.current_block.move(0, 1)
        if self.block_inside() == False or self.block_fits() == False:
            self.current_block.move(0, -1)

    def move_left(self):
        self.current_block.move(0, -1)
        if self.block_inside() == False or self.block_fits() == False:
            self.current_block.move(0, 1)

    def move_down(self):
        self.current_block.move(1, 0)
        if self.block_inside() == False or self.block_fits() == False:
            self.current_block.move(-1, 0)
            self.lock_block()

    def lock_block(self):
        tiles = self.current_block.get_new_positions()
        for position in tiles:
            self.grid.grid[position.row][position.colum] = self.current_block.id
        self.current_block = self.next_block
        self.next_block = self.get_random_block()
        self.rows_cleared = self.grid.clear_full_rows()
        self.update_score(self.rows_cleared, 0)
        if self.block_fits() == False:
            self.game_over = True

    def reset(self):
        self.grid.reset()
        self.blocks = [
            L1Block(),
            L2Block(),
            Z1Block(),
            Z2Block(),
            TBlock(),
            OBlock(),
            IBlock(),
        ]
        self.current_block = self.get_random_block()
        self.next_block = self.get_random_block()
        self.score_test = self.score
        self.score = 0
        self.runing_game = 400

    def get_highscore(self):
        with open("file.txt", "r") as fd:
            self.data = int(fd.read())

    def update_highscore(self):
        with open("file.txt", "w") as f:
            f.write(str(self.score))

    def finish(self):
        if self.score > self.data:
            self.data = self.score
            self.update_highscore()

    def block_fits(self):
        tiles = self.current_block.get_new_positions()
        for tile in tiles:
            if self.grid.is_empty(tile.row, tile.colum) == False:
                return False
        return True

    def rotate(self):
        self.current_block.rotate()
        if self.block_inside() == False or self.block_fits() == False:
            self.current_block.undo_rotate()

    def undo_rotate(self):
        self.current_block.undo_rotate()

    def block_inside(self):
        tiles = self.current_block.get_new_positions()
        for tile in tiles:
            if self.grid.is_inside(tile.row, tile.colum) == False:
                return False
        return True

    def draw(self, screen):
        self.grid.draw(screen)
        self.current_block.draw(screen, 11, 11)
        if self.next_block.id == 7:
            self.next_block.draw(screen, 255, 240)
        elif self.next_block.id == 6:
            self.next_block.draw(screen, 275, 270)
        else:
            self.next_block.draw(screen, 270, 270)


class Position:
    def __init__(self, row, colum):
        self.row = row
        self.colum = colum


class Blocks:
    def __init__(self, id):
        self.id = id
        self.cells = {}
        self.cell_size = 30
        self.row_move = 0
        self.colum_move = 0
        self.rotation_state = 0
        self.colors = Colors.get_cell_colors()

    def move(self, rows, colums):
        self.row_move += rows
        self.colum_move += colums

    def get_new_positions(self):
        tiles = self.cells[self.rotation_state]
        self.position = Position
        moved_tiles = []
        for position in tiles:
            position = Position(
                position.row + self.row_move, position.colum + self.colum_move
            )
            moved_tiles.append(position)
        return moved_tiles

    def rotate(self):
        self.rotation_state += 1
        if self.rotation_state == len(self.cells):
            self.rotation_state = 0

    def undo_rotate(self):
        if self.rotation_state == 0:
            self.rotation_state = len(self.cells) - 1
        else:
            self.rotation_state -= 1

    def draw(self, screen, offset_x, offset_y):
        tiles = self.get_new_positions()
        for tile in tiles:
            tile_rect = pygame.Rect(
                offset_x + tile.colum * self.cell_size,
                offset_y + tile.row * self.cell_size,
                self.cell_size - 1,
                self.cell_size - 1,
            )
            pygame.draw.rect(screen, self.colors[self.id], tile_rect, border_radius=3)

# List of shapes
class L1Block(Blocks):
    def __init__(self):
        super().__init__(id=1)
        self.position = Position
        self.cells = {
            0: [Position(0, 2), Position(1, 0), Position(1, 1), Position(1, 2)],
            1: [Position(0, 1), Position(1, 1), Position(2, 1), Position(2, 2)],
            2: [Position(1, 0), Position(1, 1), Position(1, 2), Position(2, 0)],
            3: [Position(0, 0), Position(0, 1), Position(1, 1), Position(2, 1)],
        }
        self.move(0, 3)


class L2Block(Blocks):
    def __init__(self):
        super().__init__(id=2)
        self.position = Position
        self.cells = {
            0: [Position(0, 0), Position(1, 0), Position(1, 1), Position(1, 2)],
            1: [Position(0, 1), Position(0, 2), Position(1, 1), Position(2, 1)],
            2: [Position(1, 0), Position(1, 1), Position(1, 2), Position(2, 2)],
            3: [Position(0, 1), Position(1, 1), Position(2, 0), Position(2, 1)],
        }
        self.move(0, 3)


class Z1Block(Blocks):
    def __init__(self):
        super().__init__(id=3)
        self.position = Position
        self.cells = {
            0: [Position(0, 0), Position(0, 1), Position(1, 1), Position(1, 2)],
            1: [Position(0, 2), Position(1, 1), Position(1, 2), Position(2, 1)],
        }
        self.move(0, 3)


class Z2Block(Blocks):
    def __init__(self):
        super().__init__(id=4)
        self.position = Position
        self.cells = {
            0: [Position(0, 1), Position(0, 2), Position(1, 0), Position(1, 1)],
            1: [Position(0, 1), Position(1, 1), Position(1, 2), Position(2, 2)],
        }
        self.move(0, 3)


class TBlock(Blocks):
    def __init__(self):
        super().__init__(id=5)
        self.position = Position
        self.cells = {
            0: [Position(0, 0), Position(0, 1), Position(0, 2), Position(1, 1)],
            1: [Position(0, 2), Position(1, 1), Position(1, 2), Position(2, 2)],
            2: [Position(1, 1), Position(2, 0), Position(2, 1), Position(2, 2)],
            3: [Position(0, 0), Position(1, 0), Position(1, 1), Position(2, 0)],
        }
        self.move(0, 3)


class OBlock(Blocks):
    def __init__(self):
        super().__init__(id=6)
        self.position = Position
        self.cells = {
            0: [Position(0, 0), Position(0, 1), Position(1, 0), Position(1, 1)]
        }
        self.move(0, 3)


class IBlock(Blocks):
    def __init__(self):
        super().__init__(id=7)
        self.position = Position
        self.cells = {
            0: [Position(1, 0), Position(1, 1), Position(1, 2), Position(1, 3)],
            1: [Position(0, 3), Position(1, 3), Position(2, 3), Position(3, 3)],
        }
        self.move(0, 3)


class ShapeWindow:
    def __init__(self, win_size, bg_color):
        self.win_size = win_size
        self.bg_color = bg_color
        self.screen = pygame.display.set_mode(win_size)
        pygame.display.set_caption("Python Tetris")
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.Font("kah-hoot.ttf", 40)
        self.scor_surface = self.title_font.render("Score", True, Colors.white)
        self.scor_rect = pygame.Rect(320, 55, 170, 60)
        self.next_surface = self.title_font.render("NEXT", True, Colors.white)
        self.next_rect = pygame.Rect(320, 200, 170, 180)
        self.record_rect = pygame.Rect(320, 480, 170, 60)
        self.record_window = pygame.Rect(320, 450, 170, 120)
        self.record = self.title_font.render("RECORD", True, Colors.white)
        self.main_window = pygame.Rect(40, 90, 260, 190)
        self.game_over_surface = self.title_font.render("GAME OVER", True, Colors.white)

    def run(self):
        grid = Grid()
        game = Game()
        down = False
        GAME_UPDATE = pygame.USEREVENT
        pygame.time.set_timer(GAME_UPDATE, 400)
        game.get_highscore()

        while True:
            if game.run() == False:
                pygame.time.set_timer(GAME_UPDATE, game.runing_game)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and not down:
                    down = True
                    if event.key == pygame.K_RETURN and game.game_over == True:
                        game.game_over = False
                        game.reset()
                    if (
                        event.key == pygame.K_ESCAPE
                        and game.game_over == False
                        and game.paused == False
                    ):
                        game.paused = True
                    if event.key == pygame.K_RETURN and game.paused == True:
                        game.paused = False
                    if (
                        event.key == pygame.K_LEFT
                        and game.game_over == False
                        and game.paused == False
                    ):
                        game.move_left()
                    if (
                        event.key == pygame.K_RIGHT
                        and game.game_over == False
                        and game.paused == False
                    ):
                        game.move_right()
                    if (
                        event.key == pygame.K_UP
                        and game.game_over == False
                        and game.paused == False
                    ):
                        game.rotate()
                if event.type == pygame.KEYUP and down:
                    down = False
                if event.type == pygame.KEYDOWN:
                    if (
                        event.key == pygame.K_DOWN
                        and game.game_over == False
                        and game.paused == False
                    ):
                        game.move_down()
                        game.move_down()
                        game.move_down()
                if (
                    event.type == GAME_UPDATE
                    and game.game_over == False
                    and game.paused == False
                ):
                    game.move_down()
            score_value_surface = self.title_font.render(
                str(game.score), True, Colors.white
            )
            self.screen.fill(self.bg_color)
            self.screen.blit(self.scor_surface, (360, 15, 50, 50))
            self.screen.blit(self.next_surface, (365, 160, 50, 50))
            self.screen.blit(self.record, (340, 410, 50, 50))

            pygame.draw.rect(self.screen, Colors.light_blue, self.scor_rect, 0, 10)
            self.screen.blit(
                score_value_surface,
                score_value_surface.get_rect(
                    centerx=self.scor_rect.centerx, centery=self.scor_rect.centery
                ),
            )
            pygame.draw.rect(self.screen, Colors.light_blue, self.next_rect, 0, 10)

            record_surface = self.title_font.render(str(game.data), True, Colors.white)
            pygame.draw.rect(self.screen, Colors.light_blue, self.record_window, 0, 10)
            self.screen.blit(
                record_surface,
                record_surface.get_rect(
                    centerx=self.record_rect.centerx, centery=self.record_rect.centery
                ),
            )
            grid.draw(self.screen)
            game.draw(self.screen)

            if game.game_over == True:
                pygame.draw.rect(self.screen, Colors.blue, self.main_window, 0, 10)
                self.screen.blit(self.game_over_surface, (80, 140, 70, 70))
                game.finish()
            if game.game_over == True or game.paused == True:
                pygame.mixer.music.pause()
            else:
                pygame.mixer.music.unpause()
            pygame.display.update()
            self.clock.tick(60)


run_win = ShapeWindow((500, 620), Colors.dark_blue)
run_win.run()
