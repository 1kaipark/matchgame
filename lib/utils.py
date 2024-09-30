import pygame
import random
import pandas as pd

from typing import Literal, Iterator

from .colors import Palette, CardPalette, MainPalette

MAX32: int = int.from_bytes(
    bytes.fromhex("7FFFFFFF")
)  # doesn't matter this is just swag lmao


"""Hopefully this is useful
https://www.pygame.org/wiki/TextWrap
"""


# draw some text into an area of a surface
# automatically wraps words
# returns any text that didn't get blitted
def drawText(surface, text, color, rect, font, aa=False, bkg=None):
    rect = pygame.Rect(rect)
    y = rect.top
    lineSpacing = -2

    # get the height of the font
    fontHeight = font.size("Tg")[1]

    while text:
        i = 1

        # determine if the row of text will be outside our area
        if y + fontHeight > rect.bottom:
            break

        # determine maximum width of line
        while font.size(text[:i])[0] < rect.width - (font.size("AA")[0]) and i < len(
            text
        ):
            i += 1  # this stops counting i when the text is too big to fit on one line

        # if we've wrapped the text, then adjust the wrap to the last word
        if i < len(text):
            i = text.rfind("", 0, i) + 1

        # render the line and blit it to the surface
        if bkg:
            image = font.render(text[:i], 1, color, bkg)
            image.set_colorkey(bkg)
        else:
            image = font.render(text[:i], aa, color)

        surface.blit(image, (rect.left, y))
        y += fontHeight + lineSpacing

        # remove the text we just blitted
        text = text[i:]

    return text


# for calculating the size of each card in 'random' mode:
def text_size(text, rect, font, padding) -> tuple[int, int]:
    """Returns tuple (width, height) of the text"""
    rect = pygame.Rect(rect)
    y = rect.top
    lineSpacing = -2

    # get the height of the font
    fontHeight = font.size("Tg")[1]

    image = font.render(text, True, (0, 0, 0))

    return (image.get_width() + padding, image.get_height() + padding)


class Card(object):
    """One card that will be displayed on screen
    Ain't writing a docstring for this one sorry yall
    """

    def __init__(
        self,
        text: str,
        match_id: str,
        x: int,
        y: int,
        width: int = 100,
        height: int = 50,
        font: "pygame.font.Font" = None,
        palette: "Palette" = CardPalette,
    ) -> None:
        """YK what it is"""

        """TODO: Optimize the colors thing. I eventually want to make a dataclass for ObjectColors and BGColors or some shit, with ones like 'default', 'highlight', 'flag', etc. 
        Also a "Position" object with .x, .y just to not have a zillion arguments
        """
        self.text = text  # display text
        self.match_id = match_id  # used to confirm match
        self.rect = pygame.Rect(x, y, width, height)
        self.palette = palette
        self._color = self.palette.bg
        self.matched = False  # is the card matched? will not display
        self.selected = False

        self.width = width
        self.height = height

        if not font:

            class LoadTheFontBro(Exception):
                pass

            raise LoadTheFontBro("Mf")

        self.font = font

    def draw(self, screen) -> None:
        """Draws rectangle on screen"""
        pygame.draw.rect(screen, self._color, self.rect)
        drawText(screen, self.text, self.palette.fg, self.rect, self.font, bkg=False)

    def check_click(self, pos) -> bool:
        """Returns if the point is inside the rectangle"""
        return self.rect.collidepoint(pos)

    def check_collision(self, rect: "pygame.Rect") -> bool:
        """Returns true if rectangle collides"""
        return self.rect.colliderect(rect) if not self.matched else False

    def set_matched(self) -> None:
        """Mark card as matched"""
        self.matched = True

    def select(self) -> None:
        """Use this to handle clicks"""
        self._color = self.palette.sel
        self.selected = True

    def deselect(self) -> None:
        """Toggle off select"""
        self._color = self.palette.bg
        self.selected = False

    def set_color(self, color) -> None:
        self._color = color


"""
how can i make a generator object GridGenerator(x_incr: int, y_incr: int): that generates a grid like
yield (idk this logic lmao) (x, y), then (x + x_incr, y + y_incr) ....

i should also make it modular, like def create_deck_from_cards(dataframe)

"""
max_attempts = 100000


def GridGenerator(
    x_incr: int,
    y_incr: int,
    x_max: int,
    y_max: int,
    positioning: Literal["grid", "random"] = "grid",
    padding: int = 20,
) -> Iterator[tuple[int, int]]:

    if positioning == "grid":
        x, y = 0, 0
        while y <= y_max or 1:
            yield (x, y)
            x += x_incr

            # Wrap around the x value if it exceeds x_max
            if x >= x_max - 150:
                x = 0
                y += y_incr
    elif positioning == "random":
        while True:
            occupied_pos: list[tuple[int, int]] = []
            attempts: int = 0
            while len(occupied_pos) < (x_max // x_incr) * (y_max // y_incr):
                if attempts >= max_attempts:
                    print("Uhhhh")
                    break
                x = random.randint(0, x_max - x_incr)
                y = random.randint(0, y_max - y_incr)
                candidate = (x, y)
                if not any(
                    (
                        (
                            abs(x - ox) < x_incr + padding
                            and abs(y - oy) < y_incr + padding
                            for ox, oy in occupied_pos
                        )
                    )
                ):
                    occupied_pos.append(candidate)
                    yield candidate
                    attempts = 0
                else:
                    attempts += 1
            else:
                break


def create_cards(
    cards_dict: dict,
    positioning: Literal["grid", "random"] = "grid",
    screen_dim: tuple = (960, 540),
    font: "pygame.font.Font" = None,
    palette: "Palette" = CardPalette,
    padding: int = 50,
) -> list["Card"]:
    if not font:

        class NoFont(Exception): ...

        raise NoFont("No Fucking Font")
    print(cards_dict)
    items: list[tuple] = list(cards_dict.items())
    random.shuffle(items)

    if positioning == "grid":
        card_width = (screen_dim[0] - 150) // 4
        card_height = screen_dim[1] // 3
    elif positioning == "random":
        card_width = (screen_dim[0] - 150) // 7
        card_height = screen_dim[1] // 6

    positions: list = (
        []
    )  # type hint would be fucked. this is a list of tuples containing 2 (x, y) positions.
    generator = GridGenerator(
        (card_width + 3),
        (card_height + 3),
        screen_dim[0],
        screen_dim[1],
        positioning=positioning,
        padding=padding,
    )

    for i in range(len(items) * 2):
        coord = next(generator)
        positions.append(coord)

    random.shuffle(positions)
    positions = list(zip(positions[::2], positions[1:][::2]))

    cards: list["Card"] = []

    for i, (key, value) in enumerate(items):

        id1 = random.randint(0, 1000)
        id2 = 1000 - id1

        pos1, pos2 = positions[i][0], positions[i][1]
        pad, _ = text_size("A", (0, 0, 100, 100), font, 0)
        term_width, term_height = (
            text_size(key, (0, 0, card_width, card_height), font, pad*2)
            if positioning == "random"
            else (card_width, card_height)
        )
        def_width, def_height = (
            text_size(value, (0, 0, card_width, card_height), font, pad*2)
            if positioning == "random"
            else (card_width, card_height)
        )

        term_card = Card(
            text=key,
            match_id=id1,
            x=pos1[0],
            y=pos1[1],
            width=term_width,
            height=term_height,
            font=font,
        )  # watch the dims
        def_card = Card(
            text=value,
            match_id=id2,
            x=pos2[0],
            y=pos2[1],
            width=def_width,
            height=def_height,
            font=font,
        )
        cards.extend([term_card, def_card])  # extend? do we want a list of lists?

    return cards


EmptyScores: pd.DataFrame = pd.DataFrame(
    columns=["fpath", "deck_name", "highscore", "_recent"]
)


def add_score_row(
    scores: pd.DataFrame,
    fpath: str,
    deck_name: str,
    highscore: float,
    recent_score: float,
) -> pd.DataFrame:
    new_row = pd.DataFrame(
        {
            "fpath": [fpath],
            "deck_name": [deck_name],
            "highscore": [highscore],
            "_recent": [recent_score],
        }
    )
    return pd.concat((scores, new_row))
