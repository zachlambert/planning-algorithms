import numpy as np
import pygame as pg
import random

class MazeGenerator:
    def __init__(self, screen_width, screen_height, resolution, cell_width, wall_width=2):
        self.resolution = resolution
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
        self.surface.fill(pg.Color("#444444"))

        self.visited = np.zeros((self.width, self.height), bool)
        self.nodes = [np.array([0, 0])]
        self.displacements = [
            np.array([-1, 0]), np.array([1, 0]),
            np.array([0, -1]), np.array([0, 1])
        ]

        self.complete = False
        self.start = None
        self.goal = None
    
    def update(self):
        if len(self.nodes) == 0:
            self.complete = True
            self.start = np.array([int(self.cell_width/2), int(self.cell_width/2)])
            self.goal = np.array([int(self.occ_map.shape[0] - self.cell_width/2),
                                  int(self.occ_map.shape[1] - self.cell_width/2)])
            return

        x, y = self.nodes[-1]
        if not self.visited[x, y]:
            for i in range(self.wall_half, self.cell_width - self.wall_half):
                for j in range(self.wall_half, self.cell_width - self.wall_half):
                    px = x*self.cell_width + i
                    py = y*self.cell_width + j
                    self.occ_map[px, py] = False
                    self.surface.fill("#FFFFFF",
                        (px*self.resolution, py*self.resolution, self.resolution, self.resolution))

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
            if node[0] < 0 or node[0] >= self.width:
                continue
            if node[1] < 0 or node[1] >= self.height:
                continue
            if not self.visited[node[0], node[1]]:
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
                self.nodes.append(node)
                valid_node = True
                break
        if not valid_node:
            self.nodes.pop()
