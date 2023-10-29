import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QMainWindow, QLabel, QPushButton, QMessageBox, QApplication, QWidget, QHBoxLayout

import twnzui
import pywinctl as pwc


class SmallWindow(QMainWindow):
    count = 0
    def __init__(self, target_title, player_name="BotPlayer"):
        super().__init__()
        SmallWindow.count += 1
        self.target_title = target_title  # Store the target window title
        self.start = False

        # Set the frameless window hint to remove the title bar
        self.setWindowFlags(Qt.FramelessWindowHint)
        # Set the window to always stay on top
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        # Set the background color to black
        palette = QPalette()
        palette.setColor(QPalette.Background, QColor(0, 0, 0))  # Black color
        self.setPalette(palette)

        self.setFixedSize(133, 16)
        self.setWindowTitle('Small Window ' + str(SmallWindow.count))
        self.player_label = QLabel(player_name, self)
        self.player_label.setStyleSheet("color: white;")

        self.start_button = QPushButton('Start', self)
        self.start_button.setFixedSize(36, 16)
        self.start_button.setStyleSheet('background: green; color: white; padding-bottom:2px;')
        self.rerender_start_button()

        self.more_button = QPushButton('⋮', self)
        self.more_button.setFixedSize(16, 16)
        self.more_button.setStyleSheet('background: grey; color: white; padding-bottom:2px;')

        # Construct Layout
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Set margin to 0 on all sides
        layout.setSpacing(0)  # Set spacing between widgets to 0
        layout.addWidget(self.start_button, alignment=Qt.AlignLeft)
        layout.addWidget(self.more_button, alignment=Qt.AlignLeft)
        layout.addStretch()
        layout.addWidget(self.player_label, alignment=Qt.AlignRight)

        # Set the layout for the central widget
        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.start_button.clicked.connect(self.on_start_clicked)
        self.more_button.clicked.connect(self.show_popup)

    def on_start_clicked(self):
        self.start = not self.start
        self.rerender_start_button()

    def rerender_start_button(self):
        if not self.start:
            t = "Start"
            ss = 'background: green; color: white; padding-bottom:2px;'
        else:
            t = "Stop"
            ss = 'background: red; color: white; padding-bottom:3px;'
        self.start_button.setText(t)
        self.start_button.setStyleSheet(ss)


    def show_popup(self):
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
            print('hitting if')
            positions.append((w.left, w.top, w.title, twnzui.utils.is_window_partially_visible(w.title)))
        else:
            # print('hitting else')
            # print(w.title)
            pass

    return positions

# Function to update the positions of small windows and handle visibility
def update_small_windows_positions(small_windows: [SmallWindow], target_wins_info: [tuple], offset=(0,0)):
    for w, p in zip(small_windows, target_wins_info):
        x, y, title, is_visible = p

        print(title)
        print(y, x, is_visible)
        # Move the small window to match the target window
        w.move(x + offset[0], y + offset[1])

        # Show/hide the small window based on target window visibility
        if is_visible:
            print('show')
            w.show()
        else:
            print('hide')
            w: SmallWindow = w
            w.hide()


if __name__ == "__main__":
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