import tkinter as tk
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

class SettingsPanel(tk.Toplevel):
    def __init__(self, root: tk.Tk, cfgfile: str = '', refresh_command: Callable = hi) -> None:
        super().__init__(root)

        self.cfgfile = cfgfile
        if self.cfgfile:
            with open(self.cfgfile, 'rb') as h:
                self.cfg = json.load(h)
        else:
            self.cfg = DEFAULTS
        
        self.refresh_command = refresh_command

        self.create_widgets()


    def create_widgets(self) -> None:
        self.labels_entries: dict = {}
        for i, key in enumerate(self.cfg.keys()):
            label = tk.Label(master=self, text=key)
            entry = tk.Entry(master=self)

            entry.insert(0, self.cfg[key])

            label.grid(row=i, column=0, sticky="w", padx=5, pady=5)
            entry.grid(row=i, column=1, padx=5, pady=5)

            self.labels_entries[label] = entry

        save_button = tk.Button(master=self, text='Save Config', command=self.save_config)
        save_button.grid(row=i+1, column=1, padx=5, pady=5)

    def save_config(self) -> None:
        new_config: dict = {label.cget('text') : ProllyFloat(entry.get()) for label, entry in self.labels_entries.items()}

        with open(self.cfgfile, 'w') as h:
            json.dump(new_config, h)

        self.refresh_command()
        
