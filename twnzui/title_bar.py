from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QStyle
from PyQt5.QtCore import Qt
from twnzui.const import *

class CustomTitleBar(QWidget):
    def __init__(self):
        super().__init__()
        self.setAutoFillBackground(True)
        self.setMouseTracking(True)  # Enable mouse tracking

        # Store the mouse press position
        self.drag_start_position = None

        # Set a specific background color (e.g., light gray)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(clr_window_bg))
        self.setPalette(palette)

        # Create minimize and close buttons
        # self.minimize_button = QPushButton('', self)
        # self.minimize_button.setIcon(self.style().standardIcon(QStyle.SP_TitleBarMinButton))
        # self.minimize_button.setStyleSheet(f"background-color: transparent; color: {clr_field_bg}")
        # self.minimize_button.clicked.connect(self.minimize_window)

        self.close_button = QPushButton('', self)
        self.close_button.setIcon(self.style().standardIcon(QStyle.SP_TitleBarCloseButton))
        self.close_button.setStyleSheet(f"background-color: transparent; color: {clr_field_bg}")
        self.close_button.clicked.connect(self.close_window)

        # Create a layout for buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)  # Push buttons to the right
        # button_layout.addWidget(self.minimize_button)
        button_layout.addWidget(self.close_button)
        button_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(button_layout)

    def minimize_window(self):
        self.window().showMinimized()

    def close_window(self):
        self.window().close()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Store the mouse press position
            self.drag_start_position = event.globalPos() - self.window().frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_start_position:
            # Move the window based on the mouse drag
            self.window().move(event.globalPos() - self.drag_start_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_start_position = None