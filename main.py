import sys
from pathlib import Path
import os
import pandas as pd

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QTreeWidget, QTreeWidgetItem, QMenuBar, QMenu, QMessageBox, QTreeWidgetItemIterator
)
from PySide6.QtGui import QAction
from PySide6.QtCore import QSize, Qt

from lib.utils import EmptyScores, MAX32
from lib.game_meta import GameMeta
from lib.q2csv import CSVGenerator
from lib.settings_panel import SettingsPanel
from matchgame import run_game





class GameLauncher(QWidget):
    """QWidget for the main window. This will show a treeview with all imported .CSV flashcard decks, with an option to play the game."""
    def __init__(self, config_path: str | None = None) -> None:
        super().__init__()

        self.deck_csvs = None
        self.scores_df = EmptyScores

        if config_path:
            self.metadata = GameMeta.from_json(config_path)

        else:
            self.metadata = GameMeta() # Initializing a default game metadata params object if no path

        self.config_path = config_path # i forgot if i ever use this lmao

        self.init_ui()

        # This is for closeEvent
        self.settings_panel = None
        self.csv_generator = None

    def init_ui(self) -> None:
        """Qt shit"""

        self.setFixedSize(QSize(400, 200))

        # Tree View for files https://doc.qt.io/qtforpython-6/tutorials/basictutorial/treewidget.html
        self.tree = QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["deck", "highscore", "recent score"])

        self.tree.itemDoubleClicked.connect(self.on_item_click) # This should open the game window

        self.load_decks_button = QPushButton("load CSVs")
        self.load_decks_button.clicked.connect(self.load_decks)

        # https://doc.qt.io/qtforpython-6/overviews/layout.html
        lt = QVBoxLayout()
        lt.addWidget(self.tree)
        lt.addWidget(self.load_decks_button)

        self.setLayout(lt)

        # menu bar
        menubar = QMenuBar(self)
        file_menu = QMenu("file", self)

        create_csv_action = QAction("quizlet to CSV", self)
        create_csv_action.triggered.connect(self.open_q2csv)
        file_menu.addAction(create_csv_action)

        settings_action = QAction("settings", self)
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)

        clear_decks_action = QAction("clear all deck files", self)
        clear_decks_action.triggered.connect(self.clear_decks)
        file_menu.addAction(clear_decks_action)

        exit_action = QAction("exit", self)
        exit_action.triggered.connect(QApplication.instance().quit)
        file_menu.addAction(exit_action)

        menubar.addMenu(file_menu)
        lt.setMenuBar(menubar)

        self.setWindowTitle("matchgame")

        # This is unnecessary, I just have it load by default. Later I gotta make a "load scores file" button
        if os.path.exists("scores.csv"):
            scores = pd.read_csv("scores.csv")
            for idx, score_row in scores.iterrows():
                try:
                    item: QTreeWidgetItem = QTreeWidgetItem(
                        [str(i) for i in [score_row['deck_name'], score_row['highscore'], score_row['_recent']]]
                    )
                    item.setData(0, Qt.UserRole, score_row['fpath']) # we need this to open the game, not going to be displayed
                    self.tree.addTopLevelItem(item)   
                except Exception as e:
                    print('ERRRMMMMMMM', e)
     
    def on_item_click(self, item: QTreeWidgetItem, column: int) -> None:
        """when u double click a tree item, should open pygame window"""
        fpath = item.data(0, Qt.UserRole)
        if fpath:
            result = run_game(fpath, self.metadata)
            # Update tree with new highscore from CSV
            if result:
                scores_updated = pd.read_csv('scores.csv')
                score = scores_updated.loc[scores_updated['fpath'] == fpath]
                print(score, "FROM MAIN")

                # for w.e reason it doesn't like floats lmao
                item.setText(1, str(result[0]))
                item.setText(2, str(result[1]))

    def load_decks(self) -> None: 
        """load deck button"""
        self.deck_csvs, _ = QFileDialog.getOpenFileNames(self, "select CSVs", "", "CSV Files (*.csv)")
        
        for csv_path in self.deck_csvs:
            deck_name = Path(csv_path).stem.strip()
            # initialize with max 32bit int
            highscore = MAX32
            recent_score = highscore
            if os.path.exists('scores.csv'):
                scores = pd.read_csv('scores.csv')
                if deck_name in scores['deck_name']:
                    highscore = scores[scores['deck_name'] == deck_name]['highscore'].item()
                    recent_score = scores[scores['deck_name'] == deck_name]['_recent'].item()

            try:
                item = QTreeWidgetItem(
                    [str(s) for s in [deck_name, highscore, recent_score]]
                )
                item.setData(0, Qt.UserRole, csv_path)
                self.tree.addTopLevelItem(item)
            except Exception as e:
                print(e)
    @property
    def csv_tree_length(self) -> int:
        """needed to count how many CSVs are there also just for the love of the game"""
        count: int = 0
        iterator = QTreeWidgetItemIterator(self.tree)

        while iterator.value():
            item = iterator.value()

            if item.parent():
                if item.parent().isExpanded():
                    count += 1
            else:
                count += 1
            iterator += 1
        
        return count

    def clear_decks(self) -> None: 
        if self.csv_tree_length > 0:
            confirm = QMessageBox(self)
            confirm.setWindowTitle("are u sure")
            confirm.setText(f"this will remove {self.csv_tree_length} decks but not delete the 'scores.csv' file.")

            confirm.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            button = confirm.exec()

            if button == QMessageBox.StandardButton.Yes:
                self.tree.clear()
            elif button == QMessageBox.StandardButton.No:
                pass
        else:
            info = QMessageBox(self)
            info.setWindowTitle("yo")
            info.setText("no CSV files loaded")
            info.exec()
    def open_q2csv(self) -> None:
        self.csv_generator = CSVGenerator()
        self.csv_generator.show()

    def open_settings(self) -> None:
        self.settings_panel = SettingsPanel(cfgfile=self.config_path, refresh_command=self.refresh_metadata)
        self.settings_panel.show()

    def refresh_metadata(self) -> None:
        self.metadata = GameMeta.from_json(self.config_path)

    def closeEvent(self, event) -> None:
        if self.settings_panel:
            self.settings_panel.close()
        if self.csv_generator:
            self.csv_generator.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = GameLauncher("defaults.json")
    launcher.show()
    sys.exit(app.exec())
