from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout

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