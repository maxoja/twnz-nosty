from PyQt5.QtGui import QPixmap, QColor, QPainter, QBitmap, QPalette
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QLineEdit, QCheckBox, QMessageBox, \
    QVBoxLayout, QLabel, QHBoxLayout, QGraphicsDropShadowEffect, QFrame
from PyQt5.QtCore import Qt, QPoint

from pocketbase import PocketBase  # Import PocketBase from your module
from twnzpb import flows
from twnzlib import resource
from twnzui.const import *
from twnzui.banner import Hammy


class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
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
        title_label = QLabel("Nosty Bot")
        title_label.setStyleSheet(f"background-color: {clr_border}; color: {clr_window_bg}; font-weight: bold; border-radius: 10px; border: 0px")
        title_label.setFixedSize(80, 20)
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
        if self.parent() is not None:
            self.parent().close()


class LoginApplication(QMainWindow):
    def __init__(self, pb_client: PocketBase, out_result: dict):
        super().__init__()
        self.pb_client = pb_client
        self.out_result = out_result

        self.setWindowFlag(Qt.FramelessWindowHint)  # Make the window frameless
        self.setAttribute(Qt.WA_TranslucentBackground)  # Make the background transparent
        self.setWindowTitle("Nosty Bot Login")

        self.wrap = QWidget(self)
        self.invisible_bar = CustomTitleBar(self.wrap)

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

        # Add an icon QLabel to display the icon image
        icon_label = Hammy(self.central_widget)
        pixmap = QPixmap('src/banner2.png')  # Load the icon image
        pixmap = pixmap.scaled(192, 64, Qt.KeepAspectRatio)  # Scale the pixmap to the desired size
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignCenter)  # Center both horizontally and vertically
        icon_label.setFixedSize(192, 64)

        # Email entry with QLineEdit
        self.email_entry = QLineEdit(self.central_widget)
        self.email_entry.setPlaceholderText("Email")
        self.email_entry.setStyleSheet(f"background: {clr_field_bg}; color: {clr_field_text}; border: none;")
        self.email_entry.setAlignment(Qt.AlignCenter)
        self.email_entry.setText(resource.load_email())

        # Password entry with QLineEdit
        self.password_entry = QLineEdit(self.central_widget)
        self.password_entry.setPlaceholderText("Password")
        self.password_entry.setEchoMode(QLineEdit.Password)
        self.password_entry.setStyleSheet(f"background: {clr_field_bg}; color: {clr_field_text}; border: none;")
        self.password_entry.setAlignment(Qt.AlignCenter)
        self.password_entry.setText(resource.load_password())

        # Remember Checkbox
        self.remember_check = QCheckBox("Remember", self.central_widget)
        self.remember_check.setChecked(resource.load_remember())

        # Account Activation Button
        self.activation_button = QPushButton("Account Activation", self.central_widget)
        self.activation_button.clicked.connect(self.perform_activation)

        # Login Button
        self.login_button = QPushButton("Login", self.central_widget)
        self.login_button.clicked.connect(self.perform_login)

        # Password Reset Button
        self.reset_button = QPushButton("Password Reset", self.central_widget)
        self.reset_button.clicked.connect(self.account_password_reset)

        # Set layout and positioning
        self.layout = QVBoxLayout(self.central_widget)
        self.row_layout = QHBoxLayout()  # Create a new QHBoxLayout for the row
        self.row_layout.addWidget(self.remember_check)
        self.row_layout.addWidget(self.activation_button)  # Add the activation button to the row
        self.layout.addWidget(icon_label)
        self.layout.addWidget(self.email_entry)
        self.layout.addWidget(self.password_entry)
        self.layout.addLayout(self.row_layout)  # Add the row layout to the main layout
        self.layout.addWidget(self.login_button)
        self.layout.addWidget(self.reset_button)
        self.layout.setAlignment(Qt.AlignCenter)

        # Set the window's position to center it
        # self.setGeometry(0, 0, 400, 300)

        # Calculate the minimal size based on the layout's contents
        self.central_widget.setLayout(self.layout)
        self.setMinimumSize(self.layout.minimumSize())
        self.center()



    def perform_login(self):
        email = self.email_entry.text()
        password = self.password_entry.text()
        remember = self.remember_check.isChecked()

        if email == "" or password == "":
            self.show_info("Info", "Please fill email and password")
            return

        auth_record = flows.login(self.pb_client, email, password)
        if auth_record is None:
            msg = ("Authentication Failed, please double-check your login details.\nContact admin if you're confident "
                   "you filled in the correct details")
            self.show_info("Failure", msg)
            return

        credits_left = flows.get_credits(self.pb_client)
        if credits_left > 0:
            msg = (f"You logged in with {credits_left} credits left.\nBot program is starting.")
            self.out_result[K_RESULT] = True
            self.show_info("Login Success", msg)

            if remember:
                resource.save_cred(email, password, remember)
            else:
                resource.save_cred('', '', False)

            self.close()
            # TODO: start the bot, show credits
        else:
            msg = f"You have no credit left, please contact admin for a top-up"
            self.show_info("Login Result", msg)

    def perform_activation(self):
        email = self.email_entry.text()

        if email == "":
            self.show_info("Info", "Please fill in your email")
            return

        flows.verify_email(self.pb_client, email)
        flows.reset_password(self.pb_client, email)
        msg = f"Send activation and password reset email to {email}\nYou'll be able to log in after verifying your email"
        self.show_info("Account Activation", msg)

    def account_password_reset(self):
        email = self.email_entry.text()

        if email == "":
            self.show_info("Info", "Please fill in your email")
            return

        flows.reset_password(self.pb_client, email)
        msg = f"Send password reset email to {email}\nYou can use the new password as soon as you reset it"
        self.show_info("Reset Password", msg)

    def show_info(self, title, message):
        QMessageBox.information(self, title, message)

    def center(self):
        frame_geometry = self.frameGeometry()
        screen_center = QApplication.desktop().screenGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())
