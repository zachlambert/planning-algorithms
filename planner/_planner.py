class Planner:
    def __init__(self, sspace):
        self.sspace = sspace

    def start(self, start, goal):
        raise NotImplementedError("Not implemented")

    def update(self):
        raise NotImplementedError("Not implemented")

    def draw(self, surface, pos=(0, 0)):
        self.sspace.draw(surface, pos)
