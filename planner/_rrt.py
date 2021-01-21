import numpy as np
from ._planner import Planner

class Vertex:
    def __init__(self, state, parent):
        self.state = state
        self.children = []
        self.parent = parent

class RRT(Planner):
    def __init__(self, sspace, K, delta_q):
        super().__init__(sspace)
        self.K = K
        self.delta_q = delta_q
        # Use an adjacency list for the graph
        # Each element is a vertex, with a list of
        # neighbours (as references)
        self.G = []
        self.sspace.create_variables(["visited"])
        self.sspace.setup_drawing("visited")
        self.k = 0
        self.complete = False
        self.path_nodes = []

    def nearest_vertex(self, state):
        closest_v = self.G[0]
        smallest_dist = self.sspace.distance(closest_v.state, state)
        for i in range(1, len(self.G)):
            dist = self.sspace.distance(self.G[i].state, state)
            if dist < smallest_dist:
                smallest_dist = dist
                closest_v = self.G[i]
        return closest_v

    def new_state(self, v, random_state):
        direction = (random_state - v.state).astype(float)
        norm = np.linalg.norm(direction)
        if norm > self.delta_q:
            direction /= norm
        state = (v.state + direction * self.delta_q).astype(int)
        return state

    def start(self, start, goal):
        self.G.append(Vertex(start, None))
        self.k = 0
        self.complete = False
        self.goal = goal

    def update(self):
        if not self.complete:
            v_new_valid = False
            new_state = None
            while not v_new_valid:
                random_state = self.sspace.random_node()
                v_near = self.nearest_vertex(random_state)
                new_state = self.new_state(v_near, random_state)
                v_new_valid = self.sspace._valid_state(new_state)
            v_new = Vertex(new_state, v_near)
            v_near.children.append(v_new)
            self.G.append(v_new)
            self.sspace.set_variable("visited", v_new.state, 1)
            self.k+=1
            if self.k == self.K:
                self.complete = True
            elif self.sspace.distance(v_new.state, self.goal) < self.delta_q:
                self.find_path(v_new)

    def find_path(self, final_vertex):
        self.path_nodes.append(self.goal)
        self.path_nodes.append(final_vertex.state)
        v = final_vertex
        while v.parent is not None:
            v = v.parent
            self.path_nodes.append(v.state)
        self.complete = True
        self.sspace.draw_path(self.path_nodes)
