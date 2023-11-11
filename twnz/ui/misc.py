from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QLabel

from twnz.const import BASE_NOSTY_TITLE
from twnz.ui.frame import NostyFrame


class MessageBox(NostyFrame):
    def __init__(self, message: str, button_text: str = "Continue", title_tail: str = " - Message Box"):
        self.message = message
        self.button_text = button_text
        NostyFrame.__init__(self, BASE_NOSTY_TITLE + title_tail, 150)

    def setup_middle(self, layout_to_add_widget: QVBoxLayout):
        self.text = QLabel(text=self.message)
        self.text.setStyleSheet("padding: 10px;")
        self.button = QPushButton()
        self.button.setText(self.button_text)
        self.button.setFixedWidth(100)
        # self.button.setStyleSheet("margin-left: 10px; margin-right: 10px")
        self.button.clicked.connect(lambda checked, label="Ok": self.close())
        layout_to_add_widget.addWidget(self.text)
        layout_to_add_widget.addWidget(self.button, alignment=Qt.AlignRight)