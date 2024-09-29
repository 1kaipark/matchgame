WIDTH, HEIGHT = 1000, 800

PENALTY = 5.0


from dataclasses import dataclass
import json


@dataclass
class GameMeta:
    screen_dim: tuple[int, int] = (WIDTH, HEIGHT)
    card_font_size: int = 20
    menu_font_size: int = 36
    penalty: float = 5.0

    @classmethod
    def from_json(cls, json_path: str):
        with open(json_path, "rb") as h:
            cfg = json.load(h)
        return cls(
            screen_dim=(cfg["width"], cfg["height"]),
            card_font_size=cfg["card_font_size"],
            menu_font_size=cfg["menu_font_size"],
            penalty=cfg["penalty"],
        )
