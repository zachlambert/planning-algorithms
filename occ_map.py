import numpy as np
import pygame as pg
import random

class OccupancyMap:
    def __init__(self, width, height, resolution, occ_color):
        self.width = int(width/resolution)
        self.height = int(height/resolution)
        self.resolution = resolution
        self.occ_map = np.full((self.width, self.height), False)
        self.surface = pg.Surface(
            (self.width*resolution, self.height*resolution))
        self.occ_color = occ_color
        self.reset()

    def reset(self):
        self.surface.fill("#FFFFFF")
        self.occ_map = np.full((self.width, self.height), False)

    def fill(self):
        self.surface.fill(self.occ_color)
        self.occ_map = np.full((self.width, self.height), True)

    def set(self, x, y, value):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        self.occ_map[x, y] = value
        if not value:
            self.surface.fill("#FFFFFF",
                (x*self.resolution, y*self.resolution,
                 self.resolution, self.resolution))
        else:
            self.surface.fill(self.occ_color,
                (x*self.resolution, y*self.resolution,
                 self.resolution, self.resolution))
        return True


class MazeGenerator:
    def __init__(self, occ_map, cell_size, wall_width=2):
        self.width = int(occ_map.width/cell_size)
        self.height = int(occ_map.height/cell_size)

        self.cell_size = cell_size
        self.wall_width = wall_width
        if self.wall_width % 2 == 1:
            self.wall_width += 1
        self.wall_half = int(wall_width/2)
        self.path_width = cell_size - wall_width

        self.visited = np.zeros((self.width, self.height), bool)
        self.nodes = [np.array([0, 0])]
        self.displacements = [
            np.array([-1, 0]), np.array([1, 0]),
            np.array([0, -1]), np.array([0, 1])
        ]

        self.complete = False
        self.start = None
        self.goal = None

        occ_map.fill()

    def fill_square(self, occ_map, node):
        for i in range(self.wall_half, self.cell_size - self.wall_half):
            for j in range(self.wall_half, self.cell_size - self.wall_half):
                occ_map.set(
                    self.cell_size*node[0] + i,
                    self.cell_size*node[1] + j,
                    False)

    def fill_gap(self, occ_map, node, disp):
        x, y = node
        for k in range(self.wall_half, self.cell_size - self.wall_half):
            for l in range(-self.wall_width, self.wall_width):
                if (disp == [1, 0]).all():
                    occ_map.set(
                        (x+1)*self.cell_size + l,
                        y*self.cell_size + k,
                        False)
                elif (disp == [-1, 0]).all():
                    occ_map.set(
                        x*self.cell_size + l,
                        y*self.cell_size + k,
                        False)
                elif (disp == [0, 1]).all():
                    occ_map.set(
                        x*self.cell_size + k,
                        (y+1)*self.cell_size + l,
                        False)
                elif (disp == [0, -1]).all():
                    occ_map.set(
                        x*self.cell_size + k,
                        y*self.cell_size + l,
                        False)

    def valid_node(self, node):
        if node[0] < 0 or node[0] >= self.width:
            return False
        if node[1] < 0 or node[1] >= self.height:
            return False
        return True

    def update(self, occ_map):
        if len(self.nodes) == 0:
            self.complete = True
            self.start = np.array([int(self.cell_size/2), int(self.cell_size/2)])
            self.goal = np.array([int(occ_map.occ_map.shape[0] - self.cell_size/2),
                                  int(occ_map.occ_map.shape[1] - self.cell_size/2)])
            return

        x, y = self.nodes[-1]
        if not self.visited[x, y]:
            self.fill_square(occ_map, self.nodes[-1])
        self.visited[x, y] = True

        valid_node = False
        indices = list(range(4))
        for i in range(3):
            k = random.randint(0, 3-i)
            end = indices[-1-i]
            indices[-1-i] = indices[k]
            indices[k] = end
        for index in indices:
            disp = self.displacements[index]
            node = self.nodes[-1] + disp
            if self.valid_node(node) and not self.visited[node[0], node[1]]:
                self.fill_gap(occ_map, self.nodes[-1], disp)
                self.nodes.append(node)
                valid_node = True
                break
        if not valid_node:
            self.nodes.pop()
