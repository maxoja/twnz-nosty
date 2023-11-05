import pystray
from PIL import Image

class NostyTray:
    def __init__(self, exit_cb=None, icon_path="src\\tray_icon.png"):
        self.exit_cb_not_none = exit_cb if exit_cb is not None else (lambda : None)
        self.menu = (pystray.MenuItem("Kill Nosty Background", self.on_exit),)
        self.icon = icon = Image.open(icon_path)
        tray_icon = pystray.Icon("nosty_bot_tray_icon", self.icon, "Nosty in the background", self.menu)
        tray_icon.run()

    def on_exit(self, icon, item):
        self.exit_cb_not_none()
        icon.stop()


if __name__ == "__main__":
    NostyTray(lambda : print("byeee"), "..\\src\\tray_icon.png")