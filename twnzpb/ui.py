import tkinter as tk
from tkinter import messagebox, PhotoImage
from tkinter import Checkbutton, BooleanVar, StringVar

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QLineEdit, QCheckBox, QMessageBox, \
    QVBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from pocketbase import PocketBase  # Import PocketBase from your module
from twnzpb import flows
from twnzlib import resource
import os

# credit for icon https://icon-icons.com/icon/random-line/72612
K_RESULT = 'result'
clr_dark_gray = '#353334'
clr_ph_text = 'grey'
clr_ph_bg = clr_dark_gray
clr_entry_text = '#CDCDCB'


class LoginApplication(QMainWindow):
    def __init__(self, pb_client: PocketBase, out_result: dict):
        super().__init__()
        self.pb_client = pb_client
        self.out_result = out_result
        self.setWindowTitle("Nosty Bot Login")

        # Create and configure the login form
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Email entry with QLineEdit
        self.email_entry = QLineEdit(self.central_widget)
        self.email_entry.setPlaceholderText("Email")
        self.email_entry.setStyleSheet(f"background: {clr_dark_gray}; color: {clr_entry_text};")
        self.email_entry.setAlignment(Qt.AlignCenter)
        self.email_entry.setText(resource.load_email())

        # Password entry with QLineEdit
        self.password_entry = QLineEdit(self.central_widget)
        self.password_entry.setPlaceholderText("Password")
        self.password_entry.setEchoMode(QLineEdit.Password)
        self.password_entry.setStyleSheet(f"background: {clr_dark_gray}; color: {clr_entry_text};")
        self.password_entry.setAlignment(Qt.AlignCenter)
        self.password_entry.setText(resource.load_password())

        # Remember Checkbox
        self.remember_check = QCheckBox("Remember", self.central_widget)
        self.remember_check.setChecked(resource.load_remember())

        # Login Button
        self.login_button = QPushButton("Login", self.central_widget)
        self.login_button.clicked.connect(self.perform_login)

        # Account Activation Button
        self.activation_button = QPushButton("Account Activation", self.central_widget)
        self.activation_button.clicked.connect(self.perform_activation)

        # Password Reset Button
        self.reset_button = QPushButton("Password Reset", self.central_widget)
        self.reset_button.clicked.connect(self.account_password_reset)

        # Set layout and positioning
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.addWidget(self.email_entry)
        self.layout.addWidget(self.password_entry)
        self.layout.addWidget(self.remember_check)
        self.layout.addWidget(self.login_button)
        self.layout.addWidget(self.activation_button)
        self.layout.addWidget(self.reset_button)
        self.setCentralWidget(self.central_widget)

        # Set the window's position to center it
        self.setGeometry(0, 0, 400, 300)
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

class PortSelectionGUI(QMainWindow):
    def __init__(self, ports: [tuple], out_port: list):
        super().__init__()
        self.ports = ports
        self.out_port = out_port
        self.button_labels = ['|'.join(p) for p in self.ports]
        self.setWindowTitle("Twnz Nosty Run")

        # Create central widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Create a label to display messages
        self.label = QLabel("", self.central_widget)

        # Create buttons from the list
        for button_label in self.button_labels:
            button = QPushButton(button_label, self.central_widget)
            button.clicked.connect(lambda checked, label=button_label: self.button_click(label))

        # Set layout and positioning
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.addWidget(self.label)
        for button in self.central_widget.findChildren(QPushButton):
            self.layout.addWidget(button)
        self.setCentralWidget(self.central_widget)

        # self.setGeometry(0, 0, 400, 300)
        self.center()

    def button_click(self, button_text):
        self.out_port.clear()
        self.out_port.append(int(button_text.split("|")[1]))
        self.label.setText(f"Button {button_text} clicked")
        self.close()

    def center(self):
        frame_geometry = self.frameGeometry()
        screen_center = QApplication.desktop().screenGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())