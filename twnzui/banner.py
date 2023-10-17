from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel


class Hammy(QLabel):
    def __init__(self, parent=None):
        QLabel.__init__(self, parent)
        self.setMouseTracking(True)  # Enable mouse tracking
        # Store the mouse press position
        self.drag_start_position = None


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
