import sys
from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QMainWindow, QLabel, QPushButton, QMessageBox, QApplication, QWidget, QHBoxLayout, QMenu, \
    QAction

import pywinctl as pwc
import twnz
import twnz.win.all
from twnz.bot.models import NostyStates


class SmallWindow(QMainWindow):
    count = 0
    def __init__(self, target_title, mode_cb=None, start_cb=None, stop_cb=None, player_name="Untitled.txt"):
        super().__init__()
        SmallWindow.count += 1
        self.target_title = target_title  # Store the target window title
        self.start = False

        self.mode_cb = mode_cb
        self.start_cb = start_cb
        self.stop_cb = stop_cb

        # Set the frameless window hint to remove the title bar
        self.setWindowFlags(Qt.FramelessWindowHint)
        # Set the window to always stay on top
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        # Set the background color to black
        palette = QPalette()
        palette.setColor(QPalette.Background, QColor(0, 0, 0))  # Black color
        self.setPalette(palette)

        self.setFixedSize(133, 16)
        self.setWindowTitle('Nosty Bot - Small Window ' + str(SmallWindow.count))
        self.player_label = QLabel(player_name, self)
        self.player_label.setStyleSheet("color: white;")

        self.start_button = QPushButton('Start', self)
        self.start_button.setFixedSize(36, 16)
        self.start_button.setStyleSheet('background: green; color: white; padding-bottom:2px;')
        self.rerender_start_button()

        self.mode_button = QPushButton('', self)
        self.mode_button.setFixedSize(16, 16)
        self.mode_button.setStyleSheet('background: grey; color: white; padding-bottom:2px;')

        self.nav_button = QPushButton(self)
        self.nav_button.setText("")
        self.nav_button.setFixedSize(16, 16)
        self.nav_button.setStyleSheet('QPushButton {background: grey; color: white; padding-bottom:2px;};')
        # self.nav_button.setStyleSheet('QPushButton::menu-indicator{ image: url(src/search_icon_tiny.png); background: grey; }; QPushButton {background: grey; color: white; padding-bottom:2px;};')

        self.nav_actions = []
        self.nav_menu = QMenu()
        self.nav_button.setMenu(self.nav_menu)

        # Create a QMenu for the dropdown options
        self.mode_menu = QMenu()
        self.mode_actions = []
        for mode in twnz.bot.enums.Mode:
            if mode != twnz.bot.enums.Mode.PHOENIX:
                # intentional for first free version
                continue
            option_action = QAction(mode, self, checkable=True)
            option_action.triggered.connect(self.on_mode_selected)
            if mode == NostyStates.INITIAL_MODE:
                option_action.setChecked(True)
            self.mode_actions.append(option_action)
            self.mode_menu.addAction(option_action)
        self.mode_button.setMenu(self.mode_menu)

        # Construct Layout
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Set margin to 0 on all sides
        layout.setSpacing(0)  # Set spacing between widgets to 0
        layout.addWidget(self.start_button, alignment=Qt.AlignLeft)
        layout.addWidget(self.mode_button, alignment=Qt.AlignLeft)
        layout.addWidget(self.nav_button, alignment=Qt.AlignLeft)
        layout.addStretch()
        layout.addWidget(self.player_label, alignment=Qt.AlignRight)

        # Set the layout for the central widget
        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.start_button.clicked.connect(self.on_start_clicked)
        self.mode_button.clicked.connect(self.show_popup)

    def on_mode_selected(self):
        action = self.sender()
        mode = action.text()

        if action in self.mode_actions:
            for menu_action in self.mode_menu.actions():
                if menu_action != action:
                    menu_action.setChecked(False)
            action.setChecked(True)

            if self.mode_cb is not None:
                self.mode_cb(twnz.bot.enums.Mode(mode))
        else:
            # show another game client
            pass

    def on_start_clicked(self, no_trigger=False):
        self.start = not self.start
        self.rerender_start_button()
        if no_trigger:
            return
        if self.start and self.start_cb is not None:
            self.start_cb()
        if not self.start and self.stop_cb is not None:
            self.stop_cb()

    def rerender_start_button(self):
        if not self.start:
            t = "Start"
            ss = 'background: green; color: white; padding-bottom:2px;'
        else:
            t = "Stop"
            ss = 'background: red; color: white; padding-bottom:3px;'
        self.start_button.setText(t)
        self.start_button.setStyleSheet(ss)

    def set_party_selector(self, new_selector_actions: List[QAction]):
        for a in self.nav_actions:
            self.nav_menu.removeAction(a)
        self.nav_actions = new_selector_actions[::]
        for a in self.nav_actions:
            self.nav_menu.addAction(a)

    def show_popup(self):
        return
        message = f"Hello from the {self.target_title} window!"
        msg_box = QMessageBox()
        msg_box.setWindowTitle('Popup Message')
        msg_box.setText(message)
        msg_box.exec_()

# Function to get the positions of target windows
def get_target_window_positions():
    windows = pwc.getAllWindows()
    positions = []
    # print('---')
    # print('\n'.join([w.title for w in windows if w.title != '']))
    # time.sleep(600000)
    for w in windows:
        if "Small Window".upper() not in w.title.upper() and ("Phoenix Bot" in w.title or "NosTale - ".upper() in w.title.upper()):
            positions.append((w.left, w.top, w.title, twnz.win.all.is_window_partially_visible(w.title)))
        else:
            # print('hitting else')
            # print(w.title)
            pass

    return positions

# Function to update the positions of small windows and handle visibility
def update_small_windows_positions(small_windows: [SmallWindow], target_wins_info: [tuple], offset=(0,0)):
    for w, p in zip(small_windows, target_wins_info):
        x, y, title, is_visible = p

        # print(title)
        # print(y, x, is_visible)
        # Move the small window to match the target window
        w.move(x + offset[0], y + offset[1])

        # Show/hide the small window based on target window visibility
        if is_visible:
            w.show()
        else:
            w: SmallWindow = w
            w.hide()


if __name__ == "__main__":
    # this is quite outdated
    app = QApplication(sys.argv)

    small_windows = [SmallWindow("Phoenix Bot"), SmallWindow("NosTale")]

    for window in small_windows:
        window.show()

    while True:
        target_wins_info = get_target_window_positions()
        update_small_windows_positions(small_windows, target_wins_info, (110, 31))
        app.processEvents()
        # time.sleep(0.01)  # Adjust the interval (in seconds) between updates as needed

    sys.exit(app.exec_())