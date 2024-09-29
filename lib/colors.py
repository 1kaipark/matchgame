from typing import Any, TypeAlias

Color: TypeAlias = tuple[int, int, int]

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

card_palette: dict = {
    "bg": (),
    "fg": (),
    "sel": (),
    "flag": (),
}

from dataclasses import dataclass


@dataclass
class Palette(object):
    bg: Color = BLACK
    fg: Color = WHITE
    sel: Color = GREEN
    flag: Color = RED

    def __getitem__(self, item) -> Color | Any:
        return getattr(self, item)


CardPalette = Palette(
    bg=(3, 155, 229),
    fg=(245, 245, 245),
    sel=(27, 94, 32),
    flag=(198, 40, 40),
)

MainPalette = Palette(
    bg=(33, 33, 33),
    fg=(255, 235, 238),
    sel=(76, 175, 80),
    flag=(216, 27, 96),
)
