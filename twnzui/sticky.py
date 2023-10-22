import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QLabel, QPushButton, QMessageBox, QApplication

import twnzui
import pywinctl as pwc


class SmallWindow(QMainWindow):
    count = 0
    def __init__(self, target_title):
        super().__init__()

        # Set the frameless window hint to remove the title bar
        # self.setWindowFlags(Qt.FramelessWindowHint)

        # Set the window to always stay on top
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        self.setGeometry(0, 0, 200, 100)  # Initial position and size
        self.setWindowTitle('Small Window ' + str(SmallWindow.count))
        SmallWindow.count += 1
        self.target_title = target_title  # Store the target window title
        label = QLabel('This is a small window', self)
        label.move(10, 10)  # Position of the label inside the window

        self.button = QPushButton('Show Popup', self)
        self.button.move(10, 60)  # Position of the button inside the window
        self.button.clicked.connect(self.show_popup)

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
def update_small_windows_positions(small_windows: [SmallWindow], target_wins_info: [tuple]):
    for w, p in zip(small_windows, target_wins_info):
        x, y, title, is_visible = p

        print(title)
        print(y, x, is_visible)
        # Move the small window to match the target window
        w.move(x, y)

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
        update_small_windows_positions(small_windows, target_wins_info)
        app.processEvents()
        # time.sleep(0.01)  # Adjust the interval (in seconds) between updates as needed

    sys.exit(app.exec_())