import tkinter as tk
from tkinter import messagebox, PhotoImage
from pocketbase import PocketBase  # Import PocketBase from your module
from twnzpb import flows
import os

class LoginApplication:
    def __init__(self, pb_client: PocketBase):
        self.pb_client = pb_client
        self.root = tk.Tk()
        self.root.title("Twnz Nosty Login")
        # self.root.iconbitmap(r'')

        icon_name = 'icon.png'
        icon_path = os.path.join('src', icon_name)
        if not os.path.isfile(icon_path):
            icon_path = os.path.join('..', 'src',  icon_name)
        if os.path.isfile(icon_path):
            self.root.tk.call('wm', 'iconphoto', self.root._w, PhotoImage(file=icon_path))

        # Create and configure the login form
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(padx=10, pady=10)

        self.email_label = tk.Label(self.login_frame, text="Email:")
        self.email_label.grid(row=0, column=0)
        self.email_entry = tk.Entry(self.login_frame)
        self.email_entry.grid(row=0, column=1)

        self.password_label = tk.Label(self.login_frame, text="Password:")
        self.password_label.grid(row=1, column=0)
        self.password_entry = tk.Entry(self.login_frame, show="*")  # Use 'show' to hide the password
        self.password_entry.grid(row=1, column=1)

        # Use lambda functions to pass parameters to login and activate_account
        self.activation_button = tk.Button(self.login_frame, text="Account Activation", command=self.perform_activation)
        self.activation_button.grid(row=2, column=0, columnspan=1, sticky="we")  # Set columnspan to 1 and sticky to "we"
        self.reset_button = tk.Button(self.login_frame, text="Password Reset", command=self.account_password_reset)
        self.reset_button.grid(row=2, column=1, columnspan=1, sticky="we")

        self.login_button = tk.Button(self.login_frame, text="Login", command=self.perform_login)
        self.login_button.grid(row=3, column=0, columnspan=2, rowspan=2,sticky="we")  # Set columnspan to 2, rowspan to 2, and sticky to "we"

        self.email_entry.focus()
        self.root.bind('<Return>', self.on_return_key)

    def perform_login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        if email == "" or password == "":
            self.show_info("Info", "Please fill email and password")
            return

        auth_record = flows.login(self.pb_client, email, password)
        if auth_record is None:
            msg = ("Authenticastion Failed, please double check your login details.\nContact admin if you're confident "
                   "you filled correct details")
            self.show_info("Failure", msg)
            return

        credits_left = flows.get_credits(pb)
        if credits_left > 0:
            msg = (f"You logged in with credit left {credits_left}\n"
                   f"Bot program is starting")
            self.show_info("Login Success", msg)
            self.root.quit()
            self.root.destroy()
            # TODO, start the bot, show credits
        else:
            msg = f"You have no credit left, please contact admin for top up"
            self.show_info("Login result", msg)


    def perform_activation(self):
        email = self.email_entry.get()

        if email == "":
            self.show_info("Info", "Please fill email")
            return

        flows.verify_email(self.pb_client, email)
        flows.reset_password(self.pb_client, email)
        msg = f"Send activation and password reset email to {email}\nYou'll be able to login after verify your email"
        self.show_info("Account Activation", msg)

    def account_password_reset(self):
        email = self.email_entry.get()

        if email == "":
            self.show_info("Info", "Please fill email")
            return

        flows.reset_password(self.pb_client, email)
        msg = f"Send password reset email to {email}\nYou can use new password as soon as you reset it"
        self.show_info("Reset Password", msg)

    def show_info(self, title, message):
        messagebox.showinfo(title, message)

    def on_return_key(self, event=None):
        self.perform_login()

    def run_mainloop(self):
        self.root.mainloop()
