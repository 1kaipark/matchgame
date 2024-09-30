import tkinter as tk
from pathlib import Path
import os

from tkinter.filedialog import askopenfilenames
from tkinter import ttk
import pandas as pd
from lib.utils import EmptyScores, MAX32
from lib.game_meta import GameMeta
from lib.q2csv import CSVGenerator

from matchgame import run_game

class Launcher(object):
    def __init__(self, root: tk.Tk, config_path: str | None = None) -> None:
        """Initialize"""
        self.root = root

        self.deck_csvs: list[str] = None
        self.scores_df: pd.DataFrame = EmptyScores
        
        if config_path:
            self.meta = GameMeta.from_json(config_path)
        else:
            self.meta = GameMeta()

        self.create_widgets()

    def create_widgets(self) -> None:
        self.tree = ttk.Treeview(master=self.root, columns=("deck_name", "highscore", "_recent"))
        # https://stackoverflow.com/questions/8688839/remove-empty-first-column-of-a-treeview-object
        self.tree['show'] = 'headings'
        self.tree.heading("deck_name", text="Deck")
        self.tree.heading("highscore", text="Highscore")
        self.tree.heading("_recent", text="Recent Score")

        self.tree.bind("<ButtonRelease-1>", self.on_item_click)

        self.open_files_button = tk.Button(master=self.root, text="Load Decks", command=self.load_decks)

        self.tree.grid(row=0, column=0)
        self.open_files_button.grid(row=1, column=0)

        self.root.resizable(False, False)
        
        
        # NOTE DELETE ME SOON
        def donothing(): 1==1
        self.menubar = tk.Menu(root)
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Clear all CSVs", command=self.clear_decks)
        self.filemenu.add_command(label="Create CSV from Quizlet", command=self.open_q2csv)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=root.quit)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        
        self.root.config(menu=self.menubar)

    def load_decks(self) -> None:
        self.deck_csvs = askopenfilenames()
        for csv in self.deck_csvs:
            csv_path = csv
            deck_name = Path(csv_path).stem.strip()

            highscore = MAX32
            recent_score = highscore

            if os.path.exists('scores.csv'):
                scores = pd.read_csv('scores.csv')
                if deck_name in list(scores['deck_name']):
                    print(deck_name, "DETECTED")
                    highscore = scores[scores['deck_name'] == deck_name]['highscore'].item()
                    recent_score = scores[scores['deck_name'] == deck_name]['_recent'].item()


            try:
                self.tree.insert(
                    "",
                    tk.END,
                    iid=csv_path,
                    values=(deck_name, highscore, recent_score)
                )
            except Exception as e:
                print(e)

    def clear_decks(self) -> None:
        self.deck_csvs = []
        for i in self.tree.get_children():
            self.tree.delete(i)
                
    def on_item_click(self, event) -> None:
        selected = self.tree.selection()
        fpath = str(*selected)
        print(fpath)
        if fpath:
            result = run_game(fpath, self.meta)
            # Update tree with new highscore from CSV
            if result:
                scores_updated = pd.read_csv('scores.csv')
                score = scores_updated.loc[scores_updated['fpath'] == selected[0]]
                print(score, "FROM MAIN")
                self.tree.item(selected, values=(Path(fpath).stem, result[1], result[0]))
                
    def open_q2csv(self) -> None:
        app = CSVGenerator(root=self.root)


if __name__ == "__main__":
    root = tk.Tk()
    app = Launcher(root, "defaults.json")
    root.mainloop()