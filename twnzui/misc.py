from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QSizePolicy, QLabel

from twnzui.frame import NostyFrame


class MessageBox(NostyFrame):
    def __init__(self, message: str):
        self.message = message
        NostyFrame.__init__(self, "Nosty Bot - Select Client", 150)

    def setup_middle(self, layout_to_add_widget: QVBoxLayout):
        self.text = QLabel(text=self.message)
        self.text.setStyleSheet("padding: 10px;")
        self.button = QPushButton()
        self.button.setText("Ok")
        self.button.setFixedWidth(100)
        # self.button.setStyleSheet("margin-left: 10px; margin-right: 10px")
        self.button.clicked.connect(lambda checked, label="Ok": self.close())
        layout_to_add_widget.addWidget(self.text)
        layout_to_add_widget.addWidget(self.button, alignment=Qt.AlignRight)
