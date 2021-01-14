import numpy as np
import random

def generate_maze(map_width, map_height, cell_width, wall_width=2):
    if wall_width % 2 == 1:
        wall_width += 1
    wall_half = int(wall_width/2)
    path_width = cell_width - wall_width

    width = int(map_width/cell_width)
    height = int(map_height/cell_width)

    occ_map = np.full((cell_width*width, cell_width*height), True)

    visited = np.zeros((width, height), bool)
    nodes = [np.array([0, 0])]
    displacements = [
        np.array([-1, 0]), np.array([1, 0]),
        np.array([0, -1]), np.array([0, 1])
    ]

    while len(nodes) != 0:
        x, y = nodes[-1]
        if not visited[x, y]:
            for i in range(wall_half, cell_width - wall_half):
                for j in range(wall_half, cell_width - wall_half):
                    occ_map[x*cell_width + i, y*cell_width + j] = False
        visited[x, y] = True


        valid_node = False
        indices = list(range(4))
        for i in range(3):
            k = random.randint(0, 3-i)
            end = indices[-1-i]
            indices[-1-i] = indices[k]
            indices[k] = end
        for index in indices:
            disp = displacements[index]
            node = nodes[-1] + disp
            if node[0] < 0 or node[0] >= width:
                continue
            if node[1] < 0 or node[1] >= height:
                continue
            if not visited[node[0], node[1]]:
                for k in range(wall_half, cell_width - wall_half):
                    for l in range(-wall_width, wall_width):
                        if (disp == [1, 0]).all():
                            occ_map[(x+1)*cell_width + l, y*cell_width + k] = False
                        elif (disp == [-1, 0]).all():
                            occ_map[x*cell_width + l, y*cell_width + k] = False
                        elif (disp == [0, 1]).all():
                            occ_map[x*cell_width + k, (y+1)*cell_width + l] = False
                        elif (disp == [0, -1]).all():
                            occ_map[x*cell_width + k, y*cell_width + l] = False
                nodes.append(node)
                valid_node = True
                break
        if not valid_node:
            nodes.pop()

    start = np.array([int(cell_width/2), int(cell_width/2)])
    goal = np.array([int(occ_map.shape[0] - cell_width/2), int(occ_map.shape[1] - cell_width/2)])

    return occ_map, start, goal
