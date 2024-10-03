"""
TODO:
Dataclasses
Start screen that allows user to select (how can I even do this?)


Eventually:
Pretty this up, maybe use sprites or something idk
"""

import pygame
import pandas as pd

import os
from pathlib import Path


from lib.colors import Palette, CardPalette, MainPalette
from lib.utils import Card, create_cards, EmptyScores, add_score_row, MAX32
from lib.game_meta import GameMeta

from typing import Literal

meta = GameMeta.from_json("defaults.json")
(WIDTH, HEIGHT), PENALTY = meta.screen_dim, meta.penalty


def load_cards(csv_path: str) -> dict:

    deck_name = Path(csv_path).stem

    cards_df = pd.read_csv(csv_path).dropna()
    cards_df = cards_df.sample(frac=1.0)
    cards_df = cards_df.iloc[0:6]

    return {t[1]["term"]: t[1]["definition"] for t in cards_df.iterrows()}, deck_name


def showGame(
    screen: "pygame.Surface",
    deck_path: str,
    palette: "Palette" = MainPalette,
    metadata: "GameMeta" = meta,
) -> tuple[float, float]:
    cards_dict, deck_name = load_cards(deck_path)

    card_font = pygame.font.Font('NotoSansKR-VariableFont_wght.ttf', metadata.card_font_size)
    menu_font = pygame.font.SysFont('Arial', metadata.menu_font_size)
    positioning = metadata.positioning
    
    cards = create_cards(
        cards_dict, positioning=positioning, screen_dim=metadata.screen_dim, font=card_font
    )

    # Handling score loading:
    highscore = MAX32
    if os.path.exists("scores.csv"):
        scores = pd.read_csv("scores.csv")
        try:
            highscore = scores[scores["deck_name"] == deck_name]["highscore"].item()
        except Exception:
            scores = add_score_row(
                scores,
                fpath=deck_path,
                deck_name=deck_name,
                highscore=highscore,
                recent_score=highscore,
            )
            scores.to_csv("scores.csv", index=False)
    else:
        scores = EmptyScores
        scores = add_score_row(
            scores,
            fpath=deck_path,
            deck_name=deck_name,
            highscore=highscore,
            recent_score=highscore,
        )
        scores.to_csv("scores.csv", index=False)

    selected: list["Card"] = []

    running: bool = True
    time_started: bool = True
    start_ticks = pygame.time.get_ticks()
    drag_card: "Card" = None
    penalty_time: float = 0

    while running:
        screen.fill(palette.bg)

        if time_started:
            current_ticks: int = pygame.time.get_ticks()
            igtime: float = (current_ticks - start_ticks) / 1000
            elapsed_time: float = round(igtime + penalty_time, 2)

        stopwatch_text = menu_font.render(f"{elapsed_time} s", True, palette.fg)
        screen.blit(stopwatch_text, (metadata.screen_dim[0] - 100, 20))

        # display the cards
        # def render_frame(screen, cards)
        for card in cards:
            if not card.matched:
                card.draw(screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if positioning == "grid":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mpos = pygame.mouse.get_pos()

                        for card in cards:
                            if card.check_click(mpos) and not card.matched:
                                card.select()
                                selected.append(card)

                                if len(selected) == 2:
                                    if (
                                        selected[0].match_id + selected[1].match_id
                                    ) == 1000:
                                        selected[0].set_matched()
                                        selected[1].set_matched()
                                    elif selected[0].match_id == selected[1].match_id:
                                        for card in selected:
                                            card.deselect()
                                    else:
                                        penalty_time += metadata.penalty
                                        x_sign = pygame.font.Font(None, 200).render(
                                            "X", True, palette.flag
                                        )
                                        x_rect = x_sign.get_rect(
                                            center=(metadata.screen_dim[0] // 2, metadata.screen_dim[1] // 2)
                                        )

                                        screen.blit(x_sign, x_rect)
                                        pygame.display.flip()
                                        pygame.time.delay(200)

                                    for card in selected:
                                        card.deselect()

                                    print([c.text for c in selected])
                                    selected = []

                elif positioning == "random":
                    mpos = pygame.mouse.get_pos()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        drag_card = None
                        for card in cards:
                            if card.check_click(mpos):
                                print(card.text, "SELECTED")
                                drag_card = card
                                drag_card.select()
                                og_coords = (drag_card.rect.x, drag_card.rect.y)
                                mx, my = event.pos
                                offset_x = card.rect.x - mx
                                offset_y = card.rect.y - my

                    elif event.type == pygame.MOUSEMOTION:
                        if drag_card:
                            mx, my = event.pos
                            drag_card.rect.x = mx + offset_x
                            drag_card.rect.y = my + offset_y

                    elif event.type == pygame.MOUSEBUTTONUP:
                        if drag_card:
                            collidedwith: list["Card"] = []
                            for card in cards:
                                if card.match_id != drag_card.match_id:
                                    if drag_card.check_collision(
                                        card.rect
                                    ):  # if any(card.check_click(coord) for coord in drag_card.corner_pos):
                                        collidedwith.append(card)

                            if len(collidedwith) > 0:
                                if not any(
                                    card.match_id + drag_card.match_id == 1000
                                    for card in collidedwith
                                ):
                                    print("NOPE")
                                    drag_card.rect.x = og_coords[0]
                                    drag_card.rect.y = og_coords[1]
                                    # handling penalty and feedback
                                    penalty_time += metadata.penalty
                                    x_sign = pygame.font.Font(None, 200).render(
                                        "X", True, palette.flag
                                    )
                                    x_rect = x_sign.get_rect(
                                        center=(metadata.screen_dim[0] // 2, metadata.screen_dim[1] // 2)
                                    )

                                    screen.blit(x_sign, x_rect)
                                    pygame.display.flip()
                                    pygame.time.delay(200)
                                else:
                                    for card in collidedwith:
                                        if card.match_id + drag_card.match_id == 1000:
                                            card.set_matched()
                                            drag_card.set_matched()
                                            cards.remove(card)
                                            cards.remove(drag_card)

                                        # if card.match_id + drag_card.match_id == 1000:
                                        #     drag_card.rect.x = og_coords[0]
                                        #     drag_card.rect.y = og_coords[1]
                                        #     card.set_matched()
                                        #     drag_card.set_matched()
                                        #     cards.remove(card)
                                        #     cards.remove(drag_card)
                                        #     # Issue: dragging onto both correct and incorrect answer -> weird error where the answer card is never deleted
                                        #     # This prevents the collision with the other incorrect card from being processed (generous handling)

                                        # else:
                                        #     # Mismatch handling: teleport the card to OG coordinates
                                        #     drag_card.rect.x = og_coords[0]
                                        #     drag_card.rect.y = og_coords[1]

                                        #     # handling penalty and feedback
                                        #     penalty_time += PENALTY
                                        #     x_sign = pygame.font.Font(None, 200).render(
                                        #         "X", True, palette.flag
                                        #     )
                                        #     x_rect = x_sign.get_rect(
                                        #         center=(WIDTH // 2, HEIGHT // 2)
                                        #     )

                                        #     screen.blit(x_sign, x_rect)
                                        #     pygame.display.flip()
                                        #     pygame.time.delay(200)

                        for card in cards:
                            card.deselect()
                        drag_card = None

        pygame.display.flip()
        if all(card.matched for card in cards):
            screen.fill(palette.bg)
            time_started = False
            ggW = menu_font.render(f"GGWP: time {elapsed_time} s", True, palette.fg)

            new_hs: bool = (elapsed_time < highscore)
            if new_hs:
                hs_congrats = menu_font.render(f"You just set a new highscore by {round(highscore - elapsed_time, 2)} s good shit brother", True, palette.fg)
                screen.blit(hs_congrats, (metadata.screen_dim[0] // 2, metadata.screen_dim[1] // 2 - 50))

            screen.blit(ggW, (metadata.screen_dim[0] // 2, metadata.screen_dim[1] // 2))
            pygame.display.flip()
            pygame.time.delay(1000)
            scores.loc[scores["deck_name"] == deck_name, "_recent"] = elapsed_time
            print(elapsed_time, highscore)
            if new_hs:
                print("New High Score")
                highscore = elapsed_time
                scores.loc[scores["deck_name"] == deck_name, "highscore"] = highscore
            scores.to_csv("scores.csv", index=False)
            print(scores)
            return (elapsed_time, highscore)


def run_game(csv_path: str, metadata: "GameMeta" = GameMeta()) -> tuple[float, float]:
    """Runs the main game loop from a given CSV path. Returns tuple (recent_score, high_score)"""
    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode((metadata.screen_dim[0], metadata.screen_dim[1]))
    pygame.display.set_caption("Hi Bro")
    font = pygame.font.Font("NotoSansKR-VariableFont_wght.ttf", metadata.card_font_size)

    score = showGame(
        screen,
        csv_path,
        metadata=metadata
    )
    print("Hi")
    pygame.time.delay(800)
    pygame.quit()
    return score


if __name__ == "__main__":
    run_game(
        "l10c2.csv", GameMeta((1280, 720), 20, 36, 6, "random")
    )
