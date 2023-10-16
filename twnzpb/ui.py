import tkinter as tk
from tkinter import messagebox, PhotoImage
from tkinter import Checkbutton, BooleanVar

from pocketbase import PocketBase  # Import PocketBase from your module
from twnzpb import flows
from twnzlib import resource
import os

# credit for icon https://icon-icons.com/icon/random-line/72612
K_RESULT = 'result'


class LoginApplication:

    def __init__(self, pb_client: PocketBase, out_result: dict):
        self.pb_client = pb_client
        self.out_result = out_result
        self.root = tk.Tk()
        self.root.title("Nosty Bot Login")
        self.root.wm_title("Nosty Bot Login")
        # Set the title bar background color to match the frame background
        self.root.overrideredirect(True)  # Remove default title bar

        self.title_bar = tk.Frame(self.root, background='#FEFBF4', height=20)
        self.title_bar.pack(fill='x')
        # Create Close and Minimize buttons on the title bar
        self.close_button = tk.Button(self.title_bar, text='X', command=self.on_close_button_click)
        self.minimize_button = tk.Button(self.title_bar, text='-', command=self.on_minimize_button_click)
        # Position Close and Minimize buttons on the title bar
        self.close_button.pack(side='right')
        self.minimize_button.pack(side='right')
        # Bind mouse events for dragging the window
        self.title_bar.bind('<ButtonPress-1>', self.on_title_bar_click)
        self.title_bar.bind('<B1-Motion>', self.on_title_bar_drag)
        # Initialize variables for tracking the window position
        self.x, self.y = 0, 0

        # Configure background color

        # self.root.protocol("WM_DELETE_WINDOW", on_destroy)
        # self.root.iconbitmap(r'')

        # Create and configure the login form
        self.login_frame = tk.Frame(self.root, background="#FEFBF4")
        self.login_frame.pack(padx=10, pady=10)

        # Define a custom style for the LoginApplication window
        self.root.tk_setPalette(background='#FEFBF4')
        # self.root.overrideredirect(True)

        icon_name = 'icon.png'
        icon_path = os.path.join('src', icon_name)
        if not os.path.isfile(icon_path):
            icon_path = os.path.join('..', 'src',  icon_name)
        if os.path.isfile(icon_path):
            self.root.tk.call('wm', 'iconphoto', self.root._w, PhotoImage(file=icon_path))

        second_color = '#353334'

        self.email_label = tk.Label(self.login_frame, text="Email:", fg=second_color)
        self.email_label.grid(row=0, column=0, sticky="w")
        self.email_entry = tk.Entry(self.login_frame, bg=second_color)
        self.email_entry.grid(row=0, column=1)
        self.email_entry.insert(0, resource.load_email())

        self.password_label = tk.Label(self.login_frame, text="Password:", fg=second_color)
        self.password_label.grid(row=1, column=0, sticky="w")
        self.password_entry = tk.Entry(self.login_frame, show="*", bg=second_color)  # Use 'show' to hide the password
        self.password_entry.grid(row=1, column=1)
        self.password_entry.insert(0, resource.load_password())

        self.remember_var = BooleanVar()
        self.remember_var.set(resource.load_remember())
        self.remember_checkbutton = Checkbutton(self.login_frame, text="Remember",
                                                variable=self.remember_var)
        self.remember_checkbutton.grid(row=2, column=1, columnspan=1, sticky="w")

        # Use lambda functions to pass parameters to login and activate_account
        self.login_button = tk.Button(self.login_frame, text="Login", command=self.perform_login)
        self.login_button.grid(row=3, column=0, columnspan=2, sticky="we")
        self.activation_button = tk.Button(self.login_frame, text="Account Activation", command=self.perform_activation)
        self.activation_button.grid(row=4, column=0, columnspan=1, sticky="we")
        self.reset_button = tk.Button(self.login_frame, text="Password Reset", command=self.account_password_reset)
        self.reset_button.grid(row=4, column=1, columnspan=1, sticky="we")

        # Get the screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculate the window position to center it on the screen
        x = (screen_width - self.root.winfo_reqwidth()) // 2
        y = (screen_height - self.root.winfo_reqheight()) // 2

        # Set the window's position to center it
        self.root.geometry(f"+{x}+{y}")

        self.email_entry.focus()
        self.root.bind('<Return>', self.on_return_key)


    def on_close_button_click(self):
        self.root.quit()
        self.root.destroy()

    def on_minimize_button_click(self):
        self.root.iconify()


    def on_title_bar_click(self, event):
        self.x, self.y = event.x, event.y

    def on_title_bar_drag(self, event):
        new_x = self.root.winfo_x() + (event.x - self.x)
        new_y = self.root.winfo_y() + (event.y - self.y)
        self.root.geometry(f"+{new_x}+{new_y}")


    def perform_login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        remember = self.remember_var.get()

        if email == "" or password == "":
            self.show_info("Info", "Please fill email and password")
            return

        auth_record = flows.login(self.pb_client, email, password)
        if auth_record is None:
            msg = ("Authenticastion Failed, please double check your login details.\nContact admin if you're confident "
                   "you filled correct details")
            self.show_info("Failure", msg)
            return

        credits_left = flows.get_credits(self.pb_client)
        if credits_left > 0:
            msg = (f"You logged in with credit left {credits_left}\n"
                   f"Bot program is starting")
            self.out_result[K_RESULT] = True
            self.show_info("Login Success", msg)

            if remember:
                resource.save_cred(email, password, remember)
            else:
                resource.save_cred('','', False)

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

class PortSelectionGUI:
    def __init__(self, ports: [tuple], out_port: list):
        self.ports = ports
        self.out_port = out_port
        # List of button labels
        self.button_labels = ['|'.join(p) for p in self.ports]

        # Create the main window
        self.root = tk.Tk()
        self.root.title("Twnz Nosty Run")

        # Create a label to display messages
        self.label = tk.Label(self.root, text="")
        self.label.pack()

        # Create buttons from the list
        for button_label in self.button_labels:
            button = tk.Button(self.root, text=button_label, command=lambda label=button_label: self.button_click(label))
            button.pack()

    def button_click(self, button_text):
        self.out_port.clear()
        self.out_port.append(int(button_text.split("|")[1]))
        self.label.config(text=f"Button {button_text} clicked")
        self.root.quit()
        self.root.destroy()

    def run_mainloop(self):
        self.root.mainloop()