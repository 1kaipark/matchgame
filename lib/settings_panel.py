from PySide6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QPushButton, QLineEdit, QLabel, QMessageBox
)
from PySide6.QtCore import QSize, Qt
from typing import Callable
import sys

import os
import json

from typing import Callable, Any

DEFAULTS: dict = {'width': 1280,
 'height': 720,
 'card_font_size': 18,
 'menu_font_size': 36,
 'penalty': 5.0,
 'positioning': 'random'}

def hi(*args, **kwargs): ...

def ProllyFloat(val: Any) -> float | Any:
    try:
        if str(float(val)) == val:
            return float(val)
        elif str(int(val)) == val:
            return int(val)
        else:
            return val
    except Exception as e:
        print(e)
        return val

class SettingsPanel(QWidget):
    def __init__(self, cfgfile: str, refresh_command: Callable) -> None:

        super().__init__()

        self.cfgfile = cfgfile
        if self.cfgfile:
            with open(self.cfgfile, 'rb') as h:
                self.cfg =json.load(h)

        else:
            self.cfg = DEFAULTS

        self.refresh_command = refresh_command
        self.init_ui()

    def init_ui(self) -> None:
        lt = QGridLayout()
        self.labels_entries: dict = {}

        for i, key in enumerate(self.cfg.keys()):
            label = QLabel(key)
            entry = QLineEdit()

            entry.setText(str(self.cfg[key]))

            lt.addWidget(label, i, 0)
            lt.addWidget(entry, i, 1)

            self.labels_entries[label] = entry

        self.save_button = QPushButton("save config")
        self.save_button.clicked.connect(self.save_config)
        lt.addWidget(self.save_button, i+1, 1)

        self.setLayout(lt)


    def save_config(self) -> None:
        new_config: dict = {
            label.text(): ProllyFloat(entry.text()) for label, entry in self.labels_entries.items()
        }
        print(new_config)
        with open(self.cfgfile, 'w') as h:
            json.dump(new_config, h)

        self.refresh_command()
        saved = QMessageBox(self)
        saved.setText("saved config to {}".format(self.cfgfile))
        button = saved.exec()
        if button == QMessageBox.StandardButton.Ok:
            self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    sp = SettingsPanel(None, lambda x: 1==1)
    sp.show()
    sys.exit(app.exec())