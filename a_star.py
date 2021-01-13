import pygame as pg
import numpy as np

class SearchSpace:
    def neighbours(self):
        raise NotImplementedError("Not implemented")
    def distance(self, node1, node2):
        raise NotImplementedError("Not implemented")
    def same_node(self, node1, node2):
        raise NotImplementedError("Not implemented")

    # Search space can record a variable for each node
    # Access by index and node. Index can be an array index, or a key for a map
    def create_variables(self, indexes):
        raise NotImplementedError("Not implemented")
    def get_variable(self, index, node):
        raise NotImplementedError("Not implemented")
    def set_variable(self, index, node, value):
        raise NotImplementedError("Not implemented")
    def draw_variable(self, surface, index):
        raise NotImplementedError("Not implemented")

class SearchSpaceGrid(SearchSpace):
    def __init__(self, occ_map):
        self.occ_map = occ_map.astype(int)
        self.offsets = [np.array([x, y])
            for x in range(-1, 2) for y in range(-1, 2) if x!=0 or y!=0]
        self.Surface = None

    def _valid_state(self, node):
        if node[0] < 0 or node[0] >= self.occ_map.shape[0]: return False
        if node[1] < 0 or node[1] >= self.occ_map.shape[1]: return False
        return self.occ_map[tuple(node)] == 0
    def neighbours(self, node):
        return [node + offset for offset in self.offsets if self._valid_state(node+offset)]
    def distance(self, node1, node2):
        return np.hypot(*(node1 - node2))
    def same_node(self, node1, node2):
        return (node1 == node2).all()

    def create_variables(self, indexes):
        self.variables = {
            index: np.zeros(self.occ_map.shape)
            for index in indexes }
    def reset_variables(self):
        for arr in self.variables.values():
            arr = np.zeros(arr.shape)
    def get_variable(self, index, node):
        return self.variables[index][tuple(node)]
    def set_variable(self, index, node, value):
        self.variables[index][tuple(node)] = value
        if index == self.draw_index:
            self.surface.fill((0, 255, 255),
                (node[0]*self.resolution, node[1]*self.resolution,
                 self.resolution, self.resolution))

    def setup_drawing(self, index, resolution):
        self.surface = pg.Surface((
            self.occ_map.shape[0]*resolution,
            self.occ_map.shape[1]*resolution), pg.SRCALPHA)
        self.draw_index = index
        self.resolution = resolution
    def draw(self, surface):
        surface.blit(self.surface, (0, 0))
    def draw_path(self, nodes):
        for node in nodes:
            self.surface.fill((255, 0, 255),
                (node[0]*self.resolution, node[1]*self.resolution,
                self.resolution, self.resolution))

class PlannerAStar:
    def __init__(self, search_space):
        self.unvisited = []
        self.sspace = search_space
        self.sspace.create_variables(["g", "h", "f", "checked"])
        self.active = False
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
        selfurface = None

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

    def setup_drawing(self, resolution):
        self.sspace.setup_drawing("g", resolution)
    def draw(self, surface):
        self.sspace.draw(surface)

