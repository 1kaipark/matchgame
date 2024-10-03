import sys
import pandas as pd

from PySide6.QtWidgets import (QApplication, QWidget, QGridLayout, QLineEdit, QPushButton, QPlainTextEdit, QLabel, QMessageBox, QFileDialog)
from PySide6.QtCore import QSize, Qt

ROW_SPLIT: str = '||||'
CARD_SPLIT: str = '~~~~'


def parse_quizlet_str(
    content: str, row_split: str = ROW_SPLIT, card_split: str = CARD_SPLIT
) -> pd.DataFrame:
    """This shit will basically take the quizlet output and parse it into a df"""
    content = content.strip().replace('\n', '')
    cards: list[str] = [
        c.strip() for c in content.split(row_split)
    ]  # This should be a list of long strings with both term and definition separated by card_split
    
    while "" in cards:
        cards.remove("")
        
    for card in cards:
        if card_split not in card:
            print("HIHIHHHIII", card)
    
    split_cards: dict = {
        card.split(card_split)[0]: card.split(card_split)[1] for card in cards
    }

    return pd.DataFrame(
        {"term": list(split_cards.keys()), "definition": list(split_cards.values())}
    )

class CSVGenerator(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.init_ui()

    def init_ui(self) -> None:
        lt = QGridLayout()

        labels_texts = ["Enter raw quizlet data:", "Front/Back Splitter String:", "Row Splitter String:"]
        for i, text in enumerate(labels_texts):
            label = QLabel(text)
            lt.addWidget(label, i, 0)
        
        # raw quizlet data: row 0
        # front back splitter: row 1
        # term def splitter: row 2

        self.content = QPlainTextEdit()

        self.card_split = QLineEdit()
        self.card_split.setText(CARD_SPLIT)

        self.row_split = QLineEdit()
        self.row_split.setText(ROW_SPLIT)

        self.process_button = QPushButton("Process Flashcards")
        self.process_button.clicked.connect(self.process_fcs)

        lt.addWidget(self.content, 0, 1)
        lt.addWidget(self.card_split, 1, 1)
        lt.addWidget(self.row_split, 2, 1)
        lt.addWidget(self.process_button, 3, 1)

        self.setLayout(lt)

    def process_fcs(self) -> None:
        content = self.content.toPlainText()
        card_split = self.card_split.text()
        row_split = self.row_split.text()

        df = parse_quizlet_str(content, row_split, card_split)
        outfile, _ = QFileDialog.getSaveFileName(self, "save CSV", "", "hi bro (*.csv)")
        df.to_csv(outfile, index=False)

        noti = QMessageBox()
        noti.setWindowTitle("saved")
        noti.setText(f"saved to {outfile}")
        noti.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    sp = CSVGenerator()
    sp.show()
    sys.exit(app.exec())