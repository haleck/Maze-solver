from generator import *
from random import choice, randint, random


class Individual:
    def __init__(self, maze) -> object:
        self.maze = maze
        self.current_cell = maze[0]
        self.current_index = 0
        self.stack = [maze[0]]
        self.route = 0
        self.individual_fitness = self.fitness()

    def fitness(self):
        return self.maze[FINISH].x - self.current_cell.x + self.maze[FINISH].y - self.current_cell.y + self.route * 0.1

    def choose_next(self) -> Cell:
        possible_cells = []
        found = False

        def check_availability(index):
            if self.stack and not self.maze[index] in self.stack:
                possible_cells.append(self.maze[index])
                return True
            elif self.stack and self.stack[-1] != self.maze[index]:
                possible_cells.append(self.maze[index])
                return True

        while not found:
            if not self.current_cell.walls['top']:
                if check_availability(self.current_index - cols):
                    found = True
            if not self.current_cell.walls['right']:
                if check_availability(self.current_index + 1):
                    found = True
            if not self.current_cell.walls['bottom']:
                if check_availability(self.current_index + cols):
                    found = True
            if not self.current_cell.walls['left']:
                if check_availability(self.current_index - 1):
                    found = True
            if not found:
                self.move_to(self.stack[-1])
                self.stack.pop()

        return choice(possible_cells)

    def move_to(self, next_cell: Cell, add=True):
        if self.current_cell == self.maze[FINISH]:
            return
        if add and self.current_cell != self.maze[0]:
            self.stack.append(self.current_cell)

        self.route += 1
        self.current_cell = next_cell
        self.current_index = next_cell.find_index(next_cell.x, next_cell.y)

    @staticmethod
    def draw_the_way(past_cell: Cell, current_cell: Cell, next_cell: Cell, color=ACTIVE_COLOR):
        x_past = past_cell.x * TILE
        y_past = past_cell.y * TILE + TOP_PADDING
        x_current = current_cell.x * TILE
        y_current = current_cell.y * TILE + TOP_PADDING
        x_next = next_cell.x * TILE
        y_next = next_cell.y * TILE + TOP_PADDING

        center = (x_current + TILE / 2, y_current + TILE / 2)
        right = (x_current + TILE, y_current + TILE / 2)
        left = (x_current, y_current + TILE / 2)
        top = (x_current + TILE / 2, y_current)
        down = (x_current + TILE / 2, y_current + TILE)

        line_width = 3

        def draw_line_to_center(start_point):
            pygame.draw.line(Maze.UI.sc, color, start_point, center, line_width)

        def draw_line_to_end_point(end_point):
            pygame.draw.line(Maze.UI.sc, color, center, end_point, line_width)
            return

        if x_current - x_past == TILE:
            draw_line_to_center(left)
            if y_current - y_next == TILE:
                draw_line_to_end_point(top)
            if y_current - y_next == -TILE:
                draw_line_to_end_point(down)
            if x_current - x_next == -TILE:
                draw_line_to_end_point(right)

        if x_current - x_past == -TILE:
            draw_line_to_center(right)
            if y_current - y_next == TILE:
                draw_line_to_end_point(top)
            if y_current - y_next == -TILE:
                draw_line_to_end_point(down)
            if x_current - x_next == TILE:
                draw_line_to_end_point(left)

        if y_current - y_past == TILE:
            draw_line_to_center(top)
            if x_current - x_next == TILE:
                draw_line_to_end_point(left)
            if x_current - x_next == -TILE:
                draw_line_to_end_point(right)
            if y_current - y_next == -TILE:
                draw_line_to_end_point(down)

        if y_current - y_past == -TILE:
            draw_line_to_center(down)
            if x_current - x_next == TILE:
                draw_line_to_end_point(left)
            if x_current - x_next == -TILE:
                draw_line_to_end_point(right)
            if y_current - y_next == TILE:
                draw_line_to_end_point(top)


class Population:
    def __init__(self, maze):
        self.maze = maze
        self.individuals = [Individual(maze) for _ in range(DEFAULT_POPULATION_SIZE)]

    def clone(self, individual: Individual):
        new_individual = Individual(self.maze)
        new_individual.current_cell = individual.current_cell
        new_individual.stack[:] = individual.stack
        new_individual.individual_fitness = individual.individual_fitness
        new_individual.route = individual.route
        return new_individual

    @staticmethod
    def sel_tournament(population, p_len):
        offspring = []
        for n in range(p_len):
            i1 = i2 = i3 = 0
            while i1 == i2 or i1 == i3 or i2 == i3:
                i1, i2, i3 = randint(0, p_len - 1), randint(0, p_len - 1), randint(0, p_len - 1)

            offspring.append(
                min([population[i1], population[i2], population[i3]], key=lambda ind: ind.individual_fitness))

        return offspring

    @staticmethod
    def cx_two_points(child1: Individual, child2: Individual):
        size = min([len(child1.stack), len(child2.stack)])
        equal = []
        for i in range(size):
            if child2.stack[i] == child1.stack[i]:
                equal.append(i)
        if len(equal) >= 2:
            point1 = equal[0]
            point2 = equal[1]
            child1.stack[point1:point2], child2.stack[point1:point2] = child2.stack[point1:point2], child1.stack[point1:point2]

    def mut(self, mutant: Individual):
        if random() <= 0.2:
            a = mutant.stack[:randint(1, len(mutant.stack) - 1)]
            mutant.stack = a
            mutant.current_cell = mutant.stack[-1]
            mutant.current_index = Cell.find_index(mutant.current_cell.x, mutant.current_cell.y)
            return

        for count in range(3):
            index2 = False
            found = False
            index1 = randint(1, len(mutant.stack) - 1)
            element = mutant.stack[index1]
            if element == self.maze[FINISH]:
                break

            for i in range(0, len(mutant.stack) - 1):
                if mutant.stack[i] == element:
                    if found:
                        index2 = i
                        break
                    else:
                        found = True

            if index1 and index2:
                if index2 < index1:
                    index1, index2 = index2, index1

                mutant_part_1 = mutant.stack[:index1]
                mutant_part_2 = mutant.stack[index2:]
                mutant.stack = mutant_part_1 + mutant_part_2
