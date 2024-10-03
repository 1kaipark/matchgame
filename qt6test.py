import sys
from pathlib import Path
import os
import pandas as pd

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QFileDialog, QTreeWidget, QTreeWidgetItem, QMenuBar, QMenu
)

from PySide6.QtGui import QAction
from PySide6.QtCore import QSize, Qt
from lib.utils import EmptyScores, MAX32
from lib.game_meta import GameMeta
from lib.q2csv import CSVGenerator
from lib.settings_panel import SettingsPanel
from matchgame import run_game


class Launcher(QWidget):
    def __init__(self, config_path: str | None = None) -> None:
        """Initialize"""
        super().__init__()
        
        self.deck_csvs = None
        self.scores_df = EmptyScores
        
        if config_path:
            self.meta = GameMeta.from_json(config_path)
        else:
            self.meta = GameMeta()

        self.config_path = config_path
        self.init_ui()

    def init_ui(self) -> None:
        self.setFixedSize(QSize(400, 200))
        # TreeView (QTreeWidget in Qt)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Deck", "Highscore", "Recent Score"])

        self.tree.itemDoubleClicked.connect(self.on_item_click)

        # Load Decks Button
        self.load_decks_button = QPushButton("Load Decks")
        self.load_decks_button.clicked.connect(self.load_decks)

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.tree)
        layout.addWidget(self.load_decks_button)
        self.setLayout(layout)

        # Menu setup
        menubar = QMenuBar(self)
        file_menu = QMenu("File", self)

        create_csv_action = QAction("Create CSV from Quizlet", self)
        create_csv_action.triggered.connect(self.open_q2csv)
        file_menu.addAction(create_csv_action)

        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)

        clear_decks_action = QAction("Clear all CSVs", self)
        clear_decks_action.triggered.connect(self.clear_decks)
        file_menu.addAction(clear_decks_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(QApplication.instance().quit)
        file_menu.addAction(exit_action)

        menubar.addMenu(file_menu)
        layout.setMenuBar(menubar)

        self.setWindowTitle("matchgame")

        # Load existing scores if 'scores.csv' exists
        if os.path.exists('scores.csv'):
            scores = pd.read_csv('scores.csv')
            for _, score_row in scores.iterrows():
                try:
                    item = QTreeWidgetItem(
                        [score_row['deck_name'], str(score_row['highscore']), str(score_row['_recent'])]
                    )
                    item.setData(0, Qt.UserRole, score_row['fpath'])
                    self.tree.addTopLevelItem(item)
                except Exception as e:
                    print(e)

    def load_decks(self) -> None:
        self.deck_csvs, _ = QFileDialog.getOpenFileNames(self, "Select CSVs", "", "CSV Files (*.csv)")

        for csv in self.deck_csvs:
            csv_path = csv
            deck_name = Path(csv_path).stem.strip()

            highscore = MAX32
            recent_score = highscore

            if os.path.exists('scores.csv'):
                scores = pd.read_csv('scores.csv')
                if deck_name in list(scores['deck_name']):
                    highscore = scores[scores['deck_name'] == deck_name]['highscore'].item()
                    recent_score = scores[scores['deck_name'] == deck_name]['_recent'].item()

            try:
                item = QTreeWidgetItem([deck_name, str(highscore), str(recent_score)])
                item.setData(0, Qt.UserRole, csv_path)
                self.tree.addTopLevelItem(item)
            except Exception as e:
                print(e)

    def clear_decks(self) -> None:
        self.tree.clear()

    def on_item_click(self, item: QTreeWidgetItem, column: int) -> None:
        fpath = item.data(0, Qt.UserRole)
        if fpath:
            result = run_game(fpath, self.meta)
            if result:
                scores_updated = pd.read_csv('scores.csv')
                score = scores_updated.loc[scores_updated['fpath'] == fpath]
                item.setText(1, str(result[1]))  # Update highscore
                item.setText(2, str(result[0]))  # Update recent score

    def open_q2csv(self) -> None:
        app = CSVGenerator(self)

    def open_settings(self) -> None:
        app = SettingsPanel(self, cfgfile=self.config_path, refresh_command=self.refresh_metadata)

    def refresh_metadata(self) -> None:
        self.meta = GameMeta.from_json(self.config_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = Launcher("defaults.json")
    launcher.show()
    sys.exit(app.exec())
