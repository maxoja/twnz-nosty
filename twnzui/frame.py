from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QMessageBox, QVBoxLayout
from PyQt5.QtCore import Qt

from twnzlib.const import BASE_NOSTY_TITLE
from twnzui.const import *
from twnzui.title_bar import CustomTitleBar


class NostyFrame(QMainWindow):
    def __init__(self, title_text: str = (BASE_NOSTY_TITLE + " Login"), label_width=80):
        super().__init__()
        self.setWindowFlag(Qt.FramelessWindowHint)  # Make the window frameless
        self.setAttribute(Qt.WA_TranslucentBackground)  # Make the background transparent
        self.setWindowTitle(BASE_NOSTY_TITLE)

        self.wrap = QWidget(self)
        self.invisible_bar = CustomTitleBar(self.wrap, title_text, label_width)

        # Create and configure the login form
        self.central_widget = QWidget(self.wrap)
        self.central_widget.setObjectName('central_widget')
        self.central_widget.setStyleSheet(
            f"#central_widget {{ background: {clr_window_bg}; border-radius: 10px; border: 1px solid {clr_border} }}")

        self.wrap_layout = QVBoxLayout()
        self.wrap_layout.addWidget(self.invisible_bar)
        self.wrap_layout.addWidget(self.central_widget)
        self.wrap.setLayout(self.wrap_layout)
        self.setCentralWidget(self.wrap)

        self.create_elems()

        # Set layout and positioning
        self.layout = QVBoxLayout(self.central_widget)
        # self.layout.addWidget(self.reset_button)
        self.setup_middle(self.layout)
        self.layout.setAlignment(Qt.AlignCenter)

        # Calculate the minimal size based on the layout's contents
        self.central_widget.setLayout(self.layout)
        self.setMinimumSize(self.layout.minimumSize())
        self.center()

    def create_elems(self):
        pass

    def setup_middle(self, layout_to_add_widget: QVBoxLayout):
        pass


    def show_info(self, title, message):
        QMessageBox.information(self, title, message)

    def center(self):
        frame_geometry = self.frameGeometry()
        screen_center = QApplication.desktop().screenGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())
