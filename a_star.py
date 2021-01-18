import pygame as pg
import numpy as np

class Planner:
    def __init__(self, sspace):
        self.sspace = sspace

    def start(self, start, goal):
        raise NotImplementedError("NotImplemented")

    def update(self):
        raise NotImplementedError("Not implemented")

    def draw(self, surface, pos=(0, 0)):
        self.sspace.draw(surface, pos)

class PlannerAStar(Planner):
    def __init__(self, search_space):
        super().__init__(search_space)
        self.unvisited = []
        self.sspace.create_variables(["g", "h", "f", "checked"])
        self.sspace.setup_drawing("g")
        self.active = False
        self.complete = False
        self.path_nodes = []

    def start(self, start, goal):
        self.start = start
        self.goal = goal
        self.num_iter = 0
        self.distance = 0
        self.sspace.reset_variables()
        self.unvisited = [self.start]
        self.initialise_node(self.start, 0)
        self.active = True
        self.complete = False

    def initialise_node(self, node, g_init):
        h = self.sspace.distance(node, self.goal)
        self.sspace.set_variable("h", node, h)
        self.update_node(node, g_init)

    def update_node(self, node, g):
        h = self.sspace.get_variable("h", node)
        f = h + g
        self.sspace.set_variable("g", node, g)
        self.sspace.set_variable("f", node, f)

    def update(self):
        if self.active:
            self.num_iter += 1
            best_f = None
            best_candidate = None
            best_i = None
            for i, candidate in enumerate(self.unvisited):
                f = self.sspace.get_variable("f", candidate)
                if best_f is None or f < best_f:
                    best_f = f
                    best_candidate = candidate
                    best_i = i

            if best_i is None:
                print("No solution found")
                self.active = False
                return

            self.unvisited.pop(best_i)
            current = best_candidate

            if self.sspace.same_node(current, self.goal):
                self.active = False
                self.find_path()
                return

            for neighbour in self.sspace.neighbours(current):
                if self.sspace.get_variable("checked", neighbour) == 0:
                    self.sspace.set_variable("checked", neighbour, 1)
                    self.unvisited.append(neighbour)
                    new_g = self.sspace.get_variable("g", current) + \
                        self.sspace.distance(current, neighbour)
                    self.initialise_node(neighbour, new_g)
                else:
                    prev_g = self.sspace.get_variable("g", neighbour)
                    new_g = self.sspace.get_variable("g", current) + \
                        self.sspace.distance(current, neighbour)
                    if new_g < prev_g:
                        self.sspace.set_variable("g", neighbour, new_g)

    def find_path(self):
        current = self.goal
        self.path_nodes.append(current)
        while not self.sspace.same_node(current, self.start):
            min_g = self.sspace.get_variable("g", current)
            next_node = None
            for neighbour in self.sspace.neighbours(current):
                if self.sspace.get_variable("checked", neighbour)==0:
                    continue
                neighbour_g = self.sspace.get_variable("g", neighbour)
                if neighbour_g < min_g:
                    min_g = neighbour_g
                    next_node = neighbour
            if next_node is None:
                break
            self.distance += 1
            current = next_node
            self.path_nodes.append(current)
        self.sspace.draw_path(self.path_nodes)
        self.complete = True
