import sys
from PySide6.QtWidgets import QLabel, QVBoxLayout, QPushButton, QWidget, QApplication
from PySide6.QtCore import Qt, QRect
from __feature__ import snake_case, true_property #type: ignore[import-not-found]

class HelloWorldApp(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.text_visible = False
        self.button_text = ('Afficher', 'Cacher')
        self.text = ('', 'HelloWorld')
        self.label = QLabel()
        self.label.object_name = 'label'
        self.label.alignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        self.button = QPushButton()
        self.button.object_name = 'button'
        self.button.text = 'Afficher'
        self.object_name = 'app'
        self.geometry = QRect(x=0, y=0, width=1000, height=1000)
        self.focus_policy = Qt.FocusPolicy.ClickFocus
        layout = QVBoxLayout()
        self.set_layout(layout)
        layout.add_widget(self.label)
        layout.add_widget(self.button)
        self.button.clicked.connect(self.changed_text)

    def changed_text(self):
        self.text_visible = not self.text_visible
        self.button.text = self.button_text[self.text_visible]
        self.label.text = self.text[self.text_visible]
        self.button_text[self.text_visible]

def main():
    app = QApplication(sys.argv)
    w = HelloWorldApp()
    w.show()
    sys.exit(app.exec())
if __name__ == '__main__':
    main()