import numpy as np
import pygame as pg
import pygame_gui as pgu
from occ_map import generate_maze
from a_star import SearchSpaceGrid, PlannerAStar

def main():

    pg.init()
    pg.display.set_caption("Path Planning")
    window = pg.display.set_mode((800, 600))

    occ_map = generate_maze(16, 12, 8, 4)

    resolution = 5
    background = pg.Surface(
        (occ_map.shape[0]*resolution, occ_map.shape[1]*resolution))
    background.fill(pg.Color("#FFFFFF"))
    for x in range(occ_map.shape[0]):
        for y in range(occ_map.shape[1]):
            if occ_map[x, y]:
                background.fill("#444444",
                    (x*resolution, y*resolution, resolution, resolution))

    start = np.array([5, 5])
    goal = np.array([15*10 + 5, 11*10 + 5])
    if occ_map[start[0], start[1]]:
        raise Exception("Invalid start position")
    if occ_map[goal[0], goal[1]]:
        raise Exception("Invalid goal position")

    sspace = SearchSpaceGrid(occ_map)
    planner = PlannerAStar(sspace)
    planner.setup_drawing(resolution)

    manager = pgu.UIManager((800, 600))
    clock = pg.time.Clock()

    start_button = pgu.elements.UIButton(
        relative_rect=pg.Rect((10, 10), (100, 40)),
        text="Start",
        manager=manager)

    while True:
        planner.update()
        dt = clock.tick()/1000.0
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.USEREVENT:
                if event.user_type == pgu.UI_BUTTON_PRESSED:
                    planner.start(start, goal)
                    start_button.kill()
            manager.process_events(event)
        manager.update(dt)

        window.blit(background, (0, 0))
        planner.draw(window)
        manager.draw_ui(window)

        pg.display.update()

if __name__ == "__main__":
    main()
