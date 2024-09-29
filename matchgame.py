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
from lib.utils import Card, create_cards, EmptyScores, add_score_row
from lib.game_meta import GameMeta

meta = GameMeta.from_json("defaults.json")
(WIDTH, HEIGHT), PENALTY = meta.screen_dim, meta.penalty


def load_cards(csv_path: str) -> dict:

    deck_name = Path(csv_path).stem

    cards_df = pd.read_csv(csv_path)
    cards_df = cards_df.sample(frac=1.0)
    cards_df = cards_df.iloc[0:10]

    return {t[1]["term"]: t[1]["definition"] for t in cards_df.iterrows()}, deck_name


def showGame(
    screen: "pygame.Surface",
    deck_path: str,
    menu_font: "pygame.font.Font",
    card_font: "pygame.font.Font",
    palette: "Palette" = MainPalette,
) -> tuple[float, float]:
    cards_dict, deck_name = load_cards(deck_path)
    cards = create_cards(
        cards_dict, positioning="grid", screen_dim=(WIDTH, HEIGHT), font=card_font
    )

    # Handling score loading:
    highscore = int.from_bytes(
        bytes.fromhex("7FFFFFFF")
    )  # doesn't matter this is just swag lmao
    if os.path.exists("scores.csv"):
        scores = pd.read_csv("scores.csv")
        try:
            highscore = scores[scores['deck_name'] == deck_name]['highscore'].item()
        except Exception:
            scores = add_score_row(scores, fpath=deck_path, deck_name=deck_name, highscore=highscore, recent_score=highscore)
            scores.to_csv('scores.csv', index=False)
    else:
        scores = EmptyScores
        scores = add_score_row(scores, fpath=deck_path, deck_name=deck_name, highscore=highscore, recent_score=highscore)
        scores.to_csv('scores.csv', index=False)

    selected: list["Card"] = []

    running: bool = True
    time_started: bool = True
    start_ticks = pygame.time.get_ticks()

    penalty_time: float = 0

    while running:
        screen.fill(palette.bg)

        if time_started:
            current_ticks: int = pygame.time.get_ticks()
            igtime: float = (current_ticks - start_ticks) / 1000
            elapsed_time: float = round(igtime + penalty_time, 2)

        stopwatch_text = menu_font.render(f"{elapsed_time} s", True, palette.fg)
        screen.blit(stopwatch_text, (WIDTH - 100, 20))

        # display the cards
        # def render_frame(screen, cards)
        for card in cards:
            if not card.matched:
                card.draw(screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

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
                                    penalty_time += PENALTY
                                    x_sign = pygame.font.Font(None, 200).render(
                                        "X", True, palette.flag
                                    )
                                    x_rect = x_sign.get_rect(
                                        center=(WIDTH // 2, HEIGHT // 2)
                                    )

                                    screen.blit(x_sign, x_rect)
                                    pygame.display.flip()
                                    pygame.time.delay(200)

                                for card in selected:
                                    card.deselect()

                                print([c.text for c in selected])
                                selected = []
        pygame.display.flip()
        if all(card.matched for card in cards):
            screen.fill(palette.bg)
            time_started = False
            ggW = menu_font.render(f"GGWP: time {elapsed_time} s", True, palette.fg)
            screen.blit(ggW, (WIDTH // 2, HEIGHT // 2))
            pygame.display.flip()
            pygame.time.delay(1000)
            scores.loc[scores['deck_name'] == deck_name, '_recent'] = elapsed_time
            print(elapsed_time, highscore)
            if elapsed_time < highscore:
                print("New High Score")
                highscore = elapsed_time
                scores.loc[scores['deck_name'] == deck_name, 'highscore'] = highscore
            scores.to_csv('scores.csv', index=False)
            print(scores)
            return (elapsed_time, highscore)


def run_game(csv_path: str) -> tuple[float, float]:
    """Runs the main game loop from a given CSV path. Returns tuple (recent_score, high_score)"""
    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Hi Bro")
    font = pygame.font.Font("NotoSansKR-VariableFont_wght.ttf", meta.card_font_size)



    score = showGame(
        screen, csv_path, pygame.font.SysFont("Roboto", meta.menu_font_size), font
    )
    print("Hi")

    pygame.quit()
    return score


if __name__ == "__main__":
    run_game("l10c2.csv")
