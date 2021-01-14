import numpy as np
import pygame as pg
import pygame_gui as pgu
from occ_map import generate_maze
from search_space import SearchSpaceGrid
from a_star import PlannerAStar

def main():

    width = 800
    height = 600
    resolution = 4

    pg.init()
    pg.display.set_caption("Path Planning")
    window = pg.display.set_mode((width, height))

    occ_map, start, goal = generate_maze(width/resolution, height/resolution, 5)

    background = pg.Surface(
        (occ_map.shape[0]*resolution, occ_map.shape[1]*resolution))
    background.fill(pg.Color("#FFFFFF"))
    for x in range(occ_map.shape[0]):
        for y in range(occ_map.shape[1]):
            if occ_map[x, y]:
                background.fill("#444444",
                    (x*resolution, y*resolution, resolution, resolution))

    sspace = SearchSpaceGrid(occ_map, resolution)

    manager = pgu.UIManager((width, height))
    clock = pg.time.Clock()

    planners = ["Wavefront", "Dikstras", "A*", "RRT*"]
    buttons = []
    button_width = 100
    button_height = 40
    button_spacing = 20
    button_box_height = len(planners)*(button_height + button_spacing) - button_spacing
    button_y = int(height/2) - int(button_box_height/2)

    for planner in planners:
        buttons.append(pgu.elements.UIButton(
            relative_rect=pg.Rect(
                (int(width/2 - button_width/2), button_y,
                 button_width, button_height)),
            text=planner,
            manager=manager
        ))
        button_y += button_height + button_spacing

    planner = None
    while True:
        if planner is not None:
            planner.update()

        dt = clock.tick()/1000.0
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.USEREVENT:
                if event.user_type == pgu.UI_BUTTON_PRESSED:
                    for i, button in enumerate(buttons):
                        if event.ui_element != button:
                            continue
                        if planners[i] == "A*":
                            planner = PlannerAStar(sspace)
                            planner.start(start, goal)
                            break
                    if planner is not None:
                        for button in buttons:
                            button.kill()
                    else:
                        print("Not implemented yet")
            manager.process_events(event)
        manager.update(dt)

        window.blit(background, (0, 0))
        if planner is not None:
            planner.draw(window)
        manager.draw_ui(window)

        pg.display.update()

if __name__ == "__main__":
    main()
