from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt, QPoint

from twnzui.const import *


class CustomTitleBar(QWidget):
    def __init__(self, parent=None, title_text:str = "Nosty Bot", label_width=80):
        super().__init__(parent)
        self.is_mouse_pressed = False
        self.mouse_position = QPoint(0, 0)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # self.setAutoFillBackground(False)
        # self.setAttribute(Qt.WA_TranslucentBackground, True)

        # self.setStyleSheet("border-radius: 10px;")
        self.setAutoFillBackground(True)
        # Create a QPalette and set the background color
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(0, 0, 0, 1))  # Set the background color and transparency
        self.setPalette(palette)

        # Add an exit button with right alignment
        exit_button = QPushButton("■")
        exit_button.clicked.connect(self.on_exit_button_clicked)
        exit_button.setStyleSheet(f"font-size: 16px; text-align: center; padding-left:0px; padding-bottom:6px;background-color: {clr_exit}; color: {clr_window_bg}; font-weight: bold; border-radius: 10px; border: 0px; text-align: center; top: 5px;")
        exit_button.setFixedSize(20, 20)


        # Add a title label with left alignment
        title_label = QLabel(title_text)
        title_label.setStyleSheet(f"background-color: {clr_border}; color: {clr_window_bg}; font-weight: bold; border-radius: 10px; border: 0px")
        title_label.setFixedSize(label_width, 20)
        title_label.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(title_label)
        self.layout.addWidget(exit_button, alignment=Qt.AlignRight)

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.is_mouse_pressed = True
            parent = self.parent()
            while parent is not None and parent.parent() is not None:
                parent = parent.parent()
            self.mouse_position = event.globalPos() - parent.frameGeometry().topLeft()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_mouse_pressed = False

    def mouseMoveEvent(self, event):
        if self.is_mouse_pressed:
            parent = self.parent()
            while parent is not None and parent.parent() is not None:
                parent = parent.parent()
            parent.move(event.globalPos() - self.mouse_position)

    def on_exit_button_clicked(self):
        self.window().close()
