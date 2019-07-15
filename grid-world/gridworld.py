import pygame, sys, random
from pygame.locals import *
from methods import *

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 82, 33)
GREY = (220, 220, 220)
DARKGREY = (128, 128, 128)
GREENGREY = (125, 164, 120)
RED = (160, 27, 16)
REDGREY = (182, 128, 109)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
GOLD = (230, 230, 138)
YELLOW = (255, 255, 0)

class GridWorld():
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Grid World")
        self.clock = pygame.time.Clock()
        self.last_tick = pygame.time.get_ticks()
        self.screen_res = [450, 450]
        self.font = pygame.font.SysFont("Calibri", 16)
        self.screen = pygame.display.set_mode(self.screen_res, pygame.HWSURFACE, 32)
        self.show_checked = True
        self.quit = False
        self.type = "dfs"
        self.new_grid()
    def new_grid(self):
        self.grid = Grid(self)
        self.agent = Agent(self.grid, self.grid.start, self.grid.goal, self.type)
        self.grid.random()
        self.run = False
    def new_random_maze(self):
        self.grid = Grid(self)
        self.agent = Agent(self.grid, self.grid.start, self.grid.goal, self.type)
        self.grid.random_maze()
        self.run = False
    def new_maze(self):
        self.grid = Grid(self)
        self.agent = Agent(self.grid, self.grid.start, self.grid.goal, self.type)
        self.grid.maze()
        self.run = False
    def loop(self):
        while True:
            self.draw()
            self.clock.tick(60)
            self.mpos = pygame.mouse.get_pos()
            if self.run:
                if self.agent.finished:
                    self.agent.show_result()
                    self.run = False
                elif self.agent.failed:
                    self.run = False
                else:
                    self.agent.make_step()
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == K_RETURN:
                        self.run = not self.run
                    if event.key == K_c:
                        self.new_grid()
                    if event.key == K_1:
                        self.grid.clear_path()
                        self.type = "dfs"
                        self.agent.new_plan(self.type)
                    if event.key == K_2:
                        self.grid.clear_path()
                        self.type = "bfs"
                        self.agent.new_plan(self.type)
                    if event.key == K_3:
                        self.grid.clear_path()
                        self.type = "ucs"
                        self.agent.new_plan(self.type)
                    if event.key == K_4:
                        self.grid.clear_path()
                        self.type = "astar"
                        self.agent.new_plan(self.type)
                    if event.key == K_m:
                        self.new_maze()
                    if event.key == K_r:
                        self.new_random_maze()
    def blitInfo(self):
        line1 = self.font.render("Press Enter to find path or pause, press 'c' to clear board", 1, WHITE)
        line2 = self.font.render("Press 1 for DFS, 2 for BFS, 3 for UCS, 4 for A*", 1, WHITE)
        line3 = self.font.render("Press 'r' to create a maze with random puddles, press 'm' to create a pure maze", 1, WHITE)
        self.screen.blit(line1, (5, 5))
        self.screen.blit(line2, (5, 20))
        self.screen.blit(line3, (5, 35))
    def draw(self):
        self.screen.fill(0)
        self.grid.update()
        self.blitInfo()
        pygame.display.update()

class Grid:
    def __init__(self, game):
        self.game = game
        self.length = int(self.game.screen_res[0]/15)
        self.width = int((self.game.screen_res[1]/15)-3)
        self.nodes = [[Node(self, [row, col+3]) for row in range(self.length)] for col in range(self.width)]
        self.row_range = self.length-3
        self.col_range = self.width+3
        self.start = (3,3)
        self.goal = (self.length-7, self.width-1)
        #self.goal = (3,3)
    def random(self):
        for col in self.nodes:
            for node in col:
                node.random_puddle()
                node.random_grass()
    def random_maze(self):
        for col in self.nodes:
            for node in col:
                node.random_puddle()
                node.random_grass()
        random_rows = [None]*random.randint(7,11)
        index = len(random_rows)
        interval = self.row_range/(index)
        beta = 1
        for i in range(len(random_rows)):
            random_rows[i] = random.randint(interval*(beta-1),interval*beta)
            beta += 1
        for i in random_rows:
            random_start_1 = random.randint(0, self.col_range/8-3)
            random_end_1 = random.randint(self.col_range/6-3, self.col_range/4-3)

            random_start_2 = random.randint(self.col_range/4-3, self.col_range*2/3-3)
            random_end_2 = random.randint(self.col_range/3-3, self.col_range/2-3)

            random_start_3 = random.randint(self.col_range/2-3,self.col_range-3)
            random_end_3 = random.randint(self.col_range*4/5-3, self.col_range)

            for j in range(random_start_1, random_end_1):
                if 0 <= i < self.row_range:
                    self.nodes[i][j].puddle = True

            for j in range(random_start_2, random_end_2):
                if 0 <= i < self.row_range:
                    self.nodes[i][j].puddle = True

            for j in range(random_start_3, random_end_3):
                if 0 <= i < self.row_range:
                    self.nodes[i][j].puddle = True
        random_cols = [None]*random.randint(7,11)
        index = len(random_cols)
        interval = self.col_range/(index)
        beta = 1
        for k in range(len(random_cols)):
            random_cols[k] = random.randint(interval*(beta-1),interval*beta)
            beta += 1
        for m in random_cols:
            random_start_1 = random.randint(0, self.row_range/8-3)
            random_end_1 = random.randint(self.row_range/6-3, self.row_range/4-3)

            random_start_2 = random.randint(self.row_range/4-3, self.row_range*2/3-3)
            random_end_2 = random.randint(self.row_range/3-3, self.row_range/2-3)

            random_start_3 = random.randint(self.row_range/2-3, self.row_range-3)
            random_end_3 = random.randint(self.row_range*4/5-3, self.row_range)

            for n in range(random_start_1, random_end_1):
                if 0 <= m < self.col_range:
                    self.nodes[n][m].puddle = True

            for n in range(random_start_2, random_end_2):
                if 0 <= m < self.row_range:
                    self.nodes[n][m].puddle = True

            for n in range(random_start_3, random_end_3):
                if 0 <= m < self.row_range:
                    self.nodes[n][m].puddle = True
        self.nodes[self.start[0]][self.start[1]].puddle = False
        self.nodes[self.goal[0]][self.goal[1]].puddle = False
    def maze(self):
        for col in self.nodes:
            for node in col:
                node.random_grass()
        random_rows = [None]*random.randint(13,16)
        index = len(random_rows)
        interval = self.row_range/(index)
        beta = 1
        for i in range(len(random_rows)):
            random_rows[i] = random.randint(interval*(beta-1),interval*beta)
            beta += 1
        for i in random_rows:
            random_start_1 = random.randint(0, self.col_range/8-3)
            random_end_1 = random.randint(self.col_range/6-3, self.col_range/4-3)

            random_start_2 = random.randint(self.col_range/4-3, self.col_range*2/3-3)
            random_end_2 = random.randint(self.col_range/3-3, self.col_range/2-3)

            random_start_3 = random.randint(self.col_range/2-3,self.col_range-3)
            random_end_3 = random.randint(self.col_range*4/5-3, self.col_range)

            for j in range(random_start_1, random_end_1):
                if 0 <= i < self.row_range:
                    self.nodes[i][j].puddle = True

            for j in range(random_start_2, random_end_2):
                if 0 <= i < self.row_range:
                    self.nodes[i][j].puddle = True

            for j in range(random_start_3, random_end_3):
                if 0 <= i < self.row_range:
                    self.nodes[i][j].puddle = True
        random_cols = [None]*random.randint(10,15)
        index = len(random_cols)
        interval = self.col_range/(index)
        beta = 1
        for k in range(len(random_cols)):
            random_cols[k] = random.randint(interval*(beta-1),interval*beta)
            beta += 1
        for m in random_cols:
            random_start_1 = random.randint(0, self.row_range/8-3)
            random_end_1 = random.randint(self.row_range/6-3, self.row_range/4-3)

            random_start_2 = random.randint(self.row_range/4-3, self.row_range*2/3-3)
            random_end_2 = random.randint(self.row_range/3-3, self.row_range/2-3)

            random_start_3 = random.randint(self.row_range/2-3, self.row_range-3)
            random_end_3 = random.randint(self.row_range*4/5-3, self.row_range)

            for n in range(random_start_1, random_end_1):
                if 0 <= m < self.col_range:
                    self.nodes[n][m].puddle = True

            for n in range(random_start_2, random_end_2):
                if 0 <= m < self.row_range:
                    self.nodes[n][m].puddle = True

            for n in range(random_start_3, random_end_3):
                if 0 <= m < self.row_range:
                    self.nodes[n][m].puddle = True
        self.nodes[self.start[0]][self.start[1]].puddle = False
        self.nodes[self.goal[0]][self.goal[1]].puddle = False
    def update(self):
        for col in self.nodes:
            for node in col:
                node.update()
                node.draw(self.game.screen)
        for i in range(self.length):
            pygame.draw.line(self.game.screen, [100]*3, (15*i, 45), (15*i, 750))
        for i in range(self.width):
            pygame.draw.line(self.game.screen, [100]*3, (0, (15*i)+45), (750, (15*i)+45))
    def clear_path(self):
        for col in self.nodes:
            for node in col:
                if node.checked:
                    node.checked = False
                if node.in_path:
                    node.in_path = False
                if node.frontier:
                    node.frontier = False

class Node():
    def __init__(self, grid, pos):
        self.grid = grid
        self.game = self.grid.game
        self.pos = pos
        self.blit_pos = [i*15 for i in self.pos]
        self.color = BLACK
        self.image = pygame.Surface((15, 15))
        self.rect = self.image.get_rect(topleft=self.blit_pos)
        self.in_path = False
        self.checked = False
        self.frontier = False
        self.puddle = False
        self.grass = False
        self.start = False
        self.goal = False
    def update(self):
        #The orders are important
        if self.puddle:
            self.color = BLUE
        elif self.start or self.goal:
            self.color = YELLOW
        elif self.in_path:
            self.color = RED
            if self.grass:
                self.color = REDGREY
        elif self.frontier:
            self.color = GREY
        elif self.checked:
            self.color = DARKGREY
            if self.grass:
                self.color = GREENGREY
        elif self.grass:
            self.color = GREEN
        elif not self.game.run:
            if pygame.mouse.get_pressed()[0] and self.rect.collidepoint(self.game.mpos):
                self.puddle = True
            if pygame.mouse.get_pressed()[2] and self.rect.collidepoint(self.game.mpos):
                self.puddle = False
        else:
            self.color = BLACK
    def random_puddle(self):
        if not random.randint(0,10) and not self.goal and not self.start:
            self.puddle = True
    def random_grass(self):
        if not random.randint(0,3) and not self.puddle:
            self.grass = True
    def cost(self):
        if self.grass:
            return 10
        else:
            return 1
    def draw(self, screen):
        self.image.fill(self.color)
        screen.blit(self.image, self.rect)

if __name__ == '__main__':
    game = GridWorld()
    game.loop()
