from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QSizePolicy

from twnzlib.const import BASE_NOSTY_TITLE
from twnzui.frame import NostyFrame

class PortSelectionGUI(NostyFrame):
    def __init__(self, ports: [tuple], out_port: list):
        self.ports = ports
        self.out_port = out_port
        NostyFrame.__init__(self, BASE_NOSTY_TITLE + " - Select Client", 150)

    def create_elems(self):
        self.button_labels = [' | '.join(p) for p in self.ports]

    def setup_middle(self, layout_to_add_widget: QVBoxLayout):
        for button_label in self.button_labels:
            button = QPushButton(button_label, self.central_widget)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            button.clicked.connect(lambda checked, label=button_label: self.button_click(label))
            layout_to_add_widget.addWidget(button)

    def button_click(self, button_text):
        self.out_port.clear()
        self.out_port.append(int(button_text.split("|")[1]))
        self.close()
