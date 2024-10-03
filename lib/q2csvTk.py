import pandas as pd
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter.filedialog import asksaveasfilename as ppppp

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


class CSVGenerator(tk.Toplevel):
    def __init__(self, root: tk.Tk) -> None:
        super().__init__(root)
        self.root = root
        self.create_widgets()
        
    def create_widgets(self) -> None:
        
        labels_texts = ["Enter raw quizlet data:", "Front/Back Splitter String:", "Row Splitter String:"]
        for i, text in enumerate(labels_texts):
            label = tk.Label(self, text=text)
            label.grid(row=i, column=0, sticky="w", padx=5, pady=5)
        self.content_entry = ScrolledText(master=self, height=10, width=30)
        # self.content_entry.insert('1.0', testcontent)
        self.content_entry.grid(row=0, column=1, padx=5, pady=5)
        

        
        self.card_split = tk.Entry(self)
        self.card_split.insert(0, CARD_SPLIT)
        self.card_split.grid(row=1, column=1, padx=5, pady=5)
        
        self.row_split = tk.Entry(self)
        self.row_split.insert(0, ROW_SPLIT)
        self.row_split.grid(row=2, column=1, padx=5, pady=5)
        
        self.process_button = tk.Button(self, text="Process Flashcards", command=self.process_flashcards)
        self.process_button.grid(row=3, columnspan=2, pady=10)
        
    def process_flashcards(self) -> None:
        content = self.content_entry.get('1.0', tk.END)
        print(content)
        card_split = self.card_split.get()
        row_split = self.row_split.get()
        df = parse_quizlet_str(content, row_split, card_split)
        df.to_csv(ppppp(defaultextension='.csv'), index=False)
        
        
        

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVGenerator(root)
    root.mainloop()
