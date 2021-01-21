import numpy as np
import pygame as pg

# This is an abstract base class for a type of state space.
# A state space is a graph, with a given distance metric between nodes.
# Each node can hold a given variable, and drawing can be setup for this
# variable, using a pygame surface

class StateSpace:
    def neighbours(self):
        raise NotImplementedError("Not implemented")
    def distance(self, node1, node2):
        raise NotImplementedError("Not implemented")
    def same_node(self, node1, node2):
        raise NotImplementedError("Not implemented")
    def random_node(self):
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


# A 2D grid is the simplest type of state space.
# It is defined by an occupancy map, where each cell is connected to its
# 8 neighbours unless the neighbour cell is occupied.

class StateSpaceGrid(StateSpace):
    def __init__(self, occ_map):
        self.occ_map = occ_map.occ_map.astype(int)
        self.offsets = [np.array([x, y])
            for x in range(-1, 2) for y in range(-1, 2) if x!=0 or y!=0]
        self.resolution = occ_map.resolution
        self.surface = pg.Surface((
            self.occ_map.shape[0]*self.resolution,
            self.occ_map.shape[1]*self.resolution), pg.SRCALPHA)

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

    def random_node(self):
        C_free = False
        node = None
        while not C_free:
            node = np.random.randint(self.occ_map.shape)
            if self._valid_state(node):
                C_free = True
        return node

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

    def setup_drawing(self, index, color=(0, 255, 255)):
        self.draw_index = index
        self.draw_color = color

    def draw(self, surface, pos=(0, 0)):
        surface.blit(self.surface, pos)

    def draw_path(self, nodes):
        for node in nodes:
            self.surface.fill((255, 0, 255),
                (node[0]*self.resolution, node[1]*self.resolution,
                self.resolution, self.resolution))
