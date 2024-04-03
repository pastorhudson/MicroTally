import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QGridLayout
from configparser import ConfigParser
from tally_server import CAMERA_CONFIG
from src.utils import build_camera_config


class ConfigEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.config = ConfigParser()
        self.config.read('config.ini')
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Config Editor')
        layout = QVBoxLayout(self)

        # Instruction label
        instructions = QLabel(
            "Add or edit configuration options. Use 'Add Option' to insert new settings. Click 'Save' to apply changes.")
        instructions.setWordWrap(True)  # Enable word wrapping for longer text
        layout.addWidget(instructions)

        self.gridLayout = QGridLayout()
        layout.addLayout(self.gridLayout)

        self.load_existing_config()

        # Buttons layout
        buttonsLayout = QVBoxLayout()
        add_btn = QPushButton('Add Option', self)
        add_btn.clicked.connect(self.add_option)
        buttonsLayout.addWidget(add_btn)

        save_btn = QPushButton('Save', self)
        save_btn.clicked.connect(self.save_config)
        buttonsLayout.addWidget(save_btn)

        layout.addLayout(buttonsLayout)

    def load_existing_config(self):
        row = self.gridLayout.rowCount()
        # Assuming 'microtallys' is the section you're working with
        section = 'microtallys'
        if self.config.has_section(section):
            for option in self.config.options(section):
                # Call add_option_row without the section parameter
                self.add_option_row(option=option, value=self.config.get(section, option), row=row)
                row += 1

    def add_option_row(self, section='', option='', value='', row=None):
        if row is None:
            row = self.gridLayout.rowCount()

        # section_edit = QLineEdit(section)
        option_name_edit = QLineEdit(option)
        option_value_edit = QLineEdit(value)

        # self.gridLayout.addWidget(section_edit, row, 0)
        self.gridLayout.addWidget(option_name_edit, row, 1)
        self.gridLayout.addWidget(option_value_edit, row, 2)

    def add_option(self):
        self.add_option_row()

    def save_config(self):
        global CAMERA_CONFIG
        print(CAMERA_CONFIG)
        self.config.clear()
        section = 'microtallys'  # Explicitly specify the section
        self.config.add_section(section)

        for row in range(self.gridLayout.rowCount()):
            option_name_item = self.gridLayout.itemAtPosition(row, 1)
            option_value_item = self.gridLayout.itemAtPosition(row, 2)

            if option_name_item and option_value_item:
                option_name = option_name_item.widget().text()
                option_value = option_value_item.widget().text()

                if not option_name:
                    continue

                self.config.set(section, option_name, option_value)

        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)
        CAMERA_CONFIG = build_camera_config()
        print(CAMERA_CONFIG)
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = ConfigEditor()
    editor.show()
    sys.exit(app.exec())
