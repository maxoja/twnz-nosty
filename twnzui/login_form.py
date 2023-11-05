from PyQt5.QtGui import QPixmap, QColor, QPainter, QBitmap, QPalette
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QLineEdit, QCheckBox, QMessageBox, \
    QVBoxLayout, QLabel, QHBoxLayout, QGraphicsDropShadowEffect, QFrame
from PyQt5.QtCore import Qt, QPoint

from pocketbase import PocketBase  # Import PocketBase from your module

from twnzlib.const import BASE_NOSTY_TITLE
from twnzpb import flows
from twnzlib import resource
from twnzui.const import *
from twnzui.banner import Hammy
from twnzui.frame import NostyFrame


class LoginResult:
    def __init__(self):
        self.success = False


class LoginApplication(NostyFrame):
    def __init__(self, pb_client: PocketBase, out: LoginResult):
        self.pb_client = pb_client
        self.out = out
        super().__init__(BASE_NOSTY_TITLE + " - Login", 120)

    def auto_login_if_possible(self):
        if len(self.email_entry.text()) > -1 and len(self.password_entry.text()) > 0:
            self.perform_login()

    def create_elems(self):
        # Add an icon QLabel to display the icon image
        self.icon_label = Hammy(self.central_widget)
        pixmap = QPixmap('src\\banner2.png')  # Load the icon image
        pixmap = pixmap.scaled(192, 64, Qt.KeepAspectRatio)  # Scale the pixmap to the desired size
        self.icon_label.setPixmap(pixmap)
        self.icon_label.setAlignment(Qt.AlignCenter)  # Center both horizontally and vertically
        self.icon_label.setFixedSize(192, 64)

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

    def setup_middle(self, layout_to_add_widget: QVBoxLayout):
        row_layout = QHBoxLayout()  # Create a new QHBoxLayout for the row
        row_layout.addWidget(self.remember_check)
        row_layout.addWidget(self.activation_button)  # Add the activation button to the row
        layout_to_add_widget.addWidget(self.icon_label)
        layout_to_add_widget.addWidget(self.email_entry)
        layout_to_add_widget.addWidget(self.password_entry)
        layout_to_add_widget.addLayout(row_layout)  # Add the row layout to the main layout
        layout_to_add_widget.addWidget(self.login_button)
        layout_to_add_widget.addWidget(self.reset_button)

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
            self.out.success = True
            self.show_info("Login Success", msg)

            if remember:
                resource.save_cred(email, password, remember)
            else:
                resource.save_cred('', '', False)

            print('closing app')
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
