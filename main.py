import numpy as np
import pygame as pg
import pygame_gui as pgu
from occ_map import MazeGenerator
from search_space import SearchSpaceGrid
from a_star import PlannerAStar

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

    def top_bar_element_rect(self, i):
        return pg.Rect((
            self.button_padding*(i+1) + self.button_width*i,
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

        self.button_reset = pgu.elements.UIButton(
            self.layout.top_bar_element_rect(2),
            text="Reset",
            manager=self.manager)

        self.resolution = 5

        self.occ_color = self.manager.get_theme().get_colour("normal_bg")

        self.maze = MazeGenerator(
            self.layout.occ_map_rect.width,
            self.layout.occ_map_rect.height,
            self.resolution,
            self.occ_color,
            5)

        self.planner = None

    def start_planner(self, planner_type):
        sspace = SearchSpaceGrid(self.maze.occ_map, self.resolution)
        if planner_type=="A*":
            self.planner = PlannerAStar(sspace)
            self.planner.start(self.maze.start, self.maze.goal)
        elif planner_type=="RRT*":
            print("Not implemented")

    def update(self, dt):
        if not self.maze.complete:
            self.maze.update()
        if self.planner is not None:
            self.planner.update()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
            if event.type == pg.USEREVENT:
                if event.user_type == pgu.UI_BUTTON_PRESSED:
                    if event.ui_element == self.button_plan and self.maze.complete:
                        self.start_planner(self.selected_planner)
                elif event.user_type == pgu.UI_DROP_DOWN_MENU_CHANGED:
                    if event.ui_element == self.drop_down_planner:
                        self.selected_planner = event.text
            self.manager.process_events(event)
        self.manager.update(dt)
        return True

    def draw(self):
        self.surface.fill(self.occ_color, self.layout.top_bar_rect)
        self.surface.blit(
            self.maze.surface,
            (self.layout.occ_map_rect.x,
             self.layout.occ_map_rect.y))
        if self.planner is not None:
            self.planner.draw(
                self.surface,
                (self.layout.occ_map_rect.x,
                 self.layout.occ_map_rect.y))
        self.manager.draw_ui(self.surface)

        pg.display.update()

def main():

    pg.init()
    pg.display.set_caption("Path Planning")
    window = Window(1200, 900)

    clock = pg.time.Clock()
    running = True
    while running:
        dt = clock.tick()/1000.0
        running = window.update(dt)
        window.draw()

if __name__ == "__main__":
    main()
