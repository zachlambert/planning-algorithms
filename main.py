import numpy as np
import pygame as pg
import pygame_gui as pgu
from sspace import OccupancyMap, MazeGenerator
from sspace import StateSpaceGrid
import planner

class WindowLayout:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.button_height = 40
        self.button_width = 100
        self.button_padding = 5

        self.top_bar_height = self.button_height + 2*self.button_padding
        self.top_bar_rect = pg.Rect((0, 0, width, self.top_bar_height))

        self.occ_map_padding = 20

        occ_map_y = 2*self.button_padding + self.button_height

        self.occ_map_rect = pg.Rect(
            (0,
             occ_map_y,
             width,
             height - occ_map_y))

    def top_bar_element_rect(self, i, right=False):
        if not right:
            return pg.Rect((
                self.button_padding*(i+1) + self.button_width*i,
                self.button_padding,
                self.button_width,
                self.button_height))
        else:
            return pg.Rect((
                self.width - (self.button_padding*(i+1) + self.button_width*(i+1)),
                self.button_padding,
                self.button_width,
                self.button_height))

class Window:
    def __init__(self, width, height):
        self.layout = WindowLayout(width, height)

        self.surface = pg.display.set_mode((width, height))
        self.manager = pgu.UIManager((width, height), "theme.json")

        # Build gui

        self.drop_down_planner = pgu.elements.UIDropDownMenu(
            ["A*", "RRT*"],
            "A*",
            relative_rect=self.layout.top_bar_element_rect(0),
            manager=self.manager)
        self.selected_planner = "A*"

        self.button_plan = pgu.elements.UIButton(
            self.layout.top_bar_element_rect(1),
            text="Plan",
            manager=self.manager)

        self.button_mode = pgu.elements.UIButton(
            self.layout.top_bar_element_rect(2),
            text="Mode = Plan",
            manager=self.manager)

        self.mode = "plan"
        self.mouse_1_down = False
        self.mouse_3_down = False

        self.button_clear = pgu.elements.UIButton(
            self.layout.top_bar_element_rect(0, True),
            text="Clear",
            manager=self.manager)

        self.button_fill = pgu.elements.UIButton(
            self.layout.top_bar_element_rect(1, True),
            text="Fill",
            manager=self.manager)

        self.button_maze = pgu.elements.UIButton(
            self.layout.top_bar_element_rect(2, True),
            text="Gen Maze",
            manager=self.manager)

        self.resolution = 5

        self.occ_color = self.manager.get_theme().get_colour("normal_bg")

        self.occ_map = OccupancyMap(
            self.layout.occ_map_rect.width,
            self.layout.occ_map_rect.height,
            self.resolution,
            self.occ_color)

        self.start = (0, 0)
        self.goal = (0, 0)

        self.maze = None
        self.planner = None

    def pos_to_node(self, pos):
        return np.array([
            int((pos[0]-self.layout.occ_map_rect.x)/self.occ_map.resolution),
            int((pos[1]-self.layout.occ_map_rect.y)/self.occ_map.resolution)
        ])

    def start_planner(self, planner_type):
        sspace = StateSpaceGrid(self.occ_map)
        start_node = self.pos_to_node(self.start)
        goal_node = self.pos_to_node(self.goal)
        if planner_type=="A*":
            self.planner = planner.AStar(sspace)
            self.planner.start(start_node, goal_node)
            return True
        elif planner_type=="RRT*":
            print("Not implemented")

        return False

    def update(self, dt):
        if self.maze is not None:
            self.maze.update(self.occ_map)
            if self.maze.complete:
                self.maze = None
                self.button_maze.set_text("Gen Maze")
        if self.planner is not None:
            self.planner.update()
            if self.planner.complete:
                self.button_plan.set_text("Clear Plan")

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
            elif event.type == pg.USEREVENT:
                if event.user_type == pgu.UI_BUTTON_PRESSED:
                    if event.ui_element == self.button_plan:
                        if self.planner is None:
                            if self.start_planner(self.selected_planner):
                                if self.maze is not None:
                                    self.maze = None
                                self.button_plan.set_text("Stop")
                        else:
                            self.planner = None
                            self.button_plan.set_text("Plan")

                    elif event.ui_element == self.button_clear:
                        self.occ_map.clear()
                    elif event.ui_element == self.button_fill:
                        self.occ_map.fill()
                    elif event.ui_element == self.button_mode:
                        if self.mode == "plan":
                            self.mode = "map"
                            self.button_mode.set_text("Mode = Map")
                        else:
                            self.mode = "plan"
                            self.button_mode.set_text("Mode = Plan")
                            self.mouse_1_down = False
                            self.mouse_3_down = False
                    elif event.ui_element == self.button_maze:
                        if self.maze is None:
                            self.maze = MazeGenerator(self.occ_map, 10)
                            self.button_maze.set_text("Stop Maze")
                        else:
                            self.maze = None
                            self.button_maze.set_text("Gen Maze")

                elif event.user_type == pgu.UI_DROP_DOWN_MENU_CHANGED:
                    if event.ui_element == self.drop_down_planner:
                        self.selected_planner = event.text

            elif event.type == pg.MOUSEBUTTONDOWN:
                if self.mode == "plan":
                    if self.occ_map.is_valid(self.pos_to_node(event.pos)):
                        if event.button == 1:
                            self.start = event.pos
                        elif event.button == 3:
                            self.goal = event.pos
                else:
                    if event.button == 1:
                        self.mouse_1_down = True
                        if self.mouse_3_down:
                            self.mouse_3_down = False
                    elif event.button == 3:
                        self.mouse_3_down = True
                        if self.mouse_1_down:
                            self.mouse_1_down = False
            elif event.type == pg.MOUSEBUTTONUP:
                if self.mode == "map":
                    if event.button == 1:
                        self.mouse_1_down = False
                    elif event.button == 3:
                        self.mouse_3_down = False

            self.manager.process_events(event)

        if self.mode == "map":
            node = self.pos_to_node(pg.mouse.get_pos())
            if self.occ_map.is_valid(node):
                if self.mouse_1_down:
                    self.occ_map.set_circle(node[0], node[1], 4, True)
                if self.mouse_3_down:
                    self.occ_map.set_circle(node[0], node[1], 4, False)

        self.manager.update(dt)
        return True

    def draw(self):
        self.surface.fill(self.occ_color, self.layout.top_bar_rect)
        self.surface.blit(
            self.occ_map.surface,
            (self.layout.occ_map_rect.x,
             self.layout.occ_map_rect.y))
        if self.planner is not None:
            self.planner.draw(
                self.surface,
                (self.layout.occ_map_rect.x,
                 self.layout.occ_map_rect.y))

        pg.draw.circle(self.surface, "#00FF00", self.start, 5)
        pg.draw.circle(self.surface, "#000000", self.start, 5, 2)
        pg.draw.circle(self.surface, "#FF0000", self.goal, 5)
        pg.draw.circle(self.surface, "#000000", self.goal, 5, 2)

        self.manager.draw_ui(self.surface)

        pg.display.update()

def main():

    pg.init()
    pg.display.set_caption("Path Planning")
    window = Window(800, 600)

    clock = pg.time.Clock()
    running = True
    while running:
        dt = clock.tick()/1000.0
        running = window.update(dt)
        window.draw()

if __name__ == "__main__":
    main()
