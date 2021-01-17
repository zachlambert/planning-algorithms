import numpy as np
import pygame as pg
import random

class MazeGenerator:
    def __init__(self, screen_width, screen_height, resolution, occ_color, cell_width, wall_width=2):
        self.resolution = resolution
        self.occ_color = occ_color

        map_width = screen_width/resolution
        map_height = screen_height/resolution

        self.cell_width = cell_width
        self.wall_width = wall_width
        if self.wall_width % 2 == 1:
            self.wall_width += 1
        self.wall_half = int(wall_width/2)
        self.path_width = cell_width - wall_width

        self.width = int(map_width/cell_width)
        self.height = int(map_height/cell_width)

        self.occ_map = np.full((cell_width*self.width, cell_width*self.height), True)

        self.surface = pg.Surface(
            (self.occ_map.shape[0]*resolution, self.occ_map.shape[1]*resolution))
        self.surface.fill(self.occ_color)

        self.visited = np.zeros((self.width, self.height), bool)
        self.nodes = [np.array([0, 0])]
        self.displacements = [
            np.array([-1, 0]), np.array([1, 0]),
            np.array([0, -1]), np.array([0, 1])
        ]

        self.complete = False
        self.start = None
        self.goal = None

    def fill_square(self, node):
        for i in range(self.wall_half, self.cell_width - self.wall_half):
            for j in range(self.wall_half, self.cell_width - self.wall_half):
                px = node[0]*self.cell_width + i
                py = node[1]*self.cell_width + j
                self.occ_map[px, py] = False
                self.surface.fill("#FFFFFF",
                    (px*self.resolution, py*self.resolution, self.resolution, self.resolution))

    def fill_gap(self, node, disp):
        x, y = node
        for k in range(self.wall_half, self.cell_width - self.wall_half):
            for l in range(-self.wall_width, self.wall_width):
                if (disp == [1, 0]).all():
                    px = (x+1)*self.cell_width + l
                    py = y*self.cell_width + k
                elif (disp == [-1, 0]).all():
                    px = x*self.cell_width + l
                    py = y*self.cell_width + k
                elif (disp == [0, 1]).all():
                    px = x*self.cell_width + k
                    py = (y+1)*self.cell_width + l
                elif (disp == [0, -1]).all():
                    px = x*self.cell_width + k
                    py = y*self.cell_width + l
                self.occ_map[px, py] = False
                self.surface.fill("#FFFFFF",
                    (px*self.resolution, py*self.resolution, self.resolution, self.resolution))

    def valid_node(self, node):
        if node[0] < 0 or node[0] >= self.width:
            return False
        if node[1] < 0 or node[1] >= self.height:
            return False
        return True

    def update(self):
        if len(self.nodes) == 0:
            self.complete = True
            self.start = np.array([int(self.cell_width/2), int(self.cell_width/2)])
            self.goal = np.array([int(self.occ_map.shape[0] - self.cell_width/2),
                                  int(self.occ_map.shape[1] - self.cell_width/2)])
            return

        x, y = self.nodes[-1]
        if not self.visited[x, y]:
            self.fill_square(self.nodes[-1])
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
                self.fill_gap(self.nodes[-1], disp)
                self.nodes.append(node)
                valid_node = True
                break
        if not valid_node:
            self.nodes.pop()
