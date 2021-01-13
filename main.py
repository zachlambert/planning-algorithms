import pygame as pg
import pygame_gui as pgu
from occ_map import generate_maze

def main():

    pg.init()
    pg.display.set_caption("Path Planning")
    window = pg.display.set_mode((800, 600))

    occ_map = generate_maze(8, 6, 80, 40)

    background = pg.Surface(occ_map.shape)
    background.fill(pg.Color("#FFFFFF"))
    for x in range(occ_map.shape[0]):
        for y in range(occ_map.shape[1]):
            if occ_map[x, y]:
                background.set_at((x, y), "#444444")

    manager = pgu.UIManager((800, 600))
    clock = pg.time.Clock()

    button = pgu.elements.UIButton(
        relative_rect=pg.Rect((10, 10), (100, 40)),
        text="Start",
        manager=manager)

    while True:
        dt = clock.tick(60)/1000.0
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.USEREVENT:
                if event.user_type == pgu.UI_BUTTON_PRESSED:
                    print("Starting")
            manager.process_events(event)

        manager.update(dt)

        window.blit(background, (0, 0))
        manager.draw_ui(window)

        pg.display.update()

if __name__ == "__main__":
    main()
