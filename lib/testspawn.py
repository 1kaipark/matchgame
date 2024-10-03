from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout


class bullshi(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.init_ui()

    def init_ui(self) -> None:
        self.label = QLabel("Helo")
        lt = QVBoxLayout()
        lt.addWidget(self.label)
        self.setLayout(lt)
