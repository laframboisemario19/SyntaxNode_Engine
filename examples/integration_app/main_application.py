import sys
from PySide6.QtWidgets import QLabel, QVBoxLayout, QPushButton, QFrame, QWidget, QApplication
from PySide6.QtCore import Qt, QRect
from __feature__ import snake_case, true_property #type: ignore[import-not-found]

class IntegrationApp(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.click_count = 0
        self.is_active = False
        self.title_label = QLabel()
        self.title_label.object_name = 'title_label'
        self.title_label.text = 'Validation du générateur AST PySide6'
        self.title_label.alignment = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
        self.title_label.word_wrap = True
        self.title_label.margin = 10
        self.separator_frame = QFrame()
        self.separator_frame.object_name = 'separator_frame'
        self.separator_frame.frame_shape = QFrame.Shape.HLine
        self.separator_frame.frame_shadow = QFrame.Shadow.Sunken
        self.separator_frame.line_width = 2
        self.counter_label = QLabel()
        self.counter_label.object_name = 'counter_label'
        self.counter_label.text = 'Clics : 0 - Actif : False'
        self.action_btn = QPushButton()
        self.action_btn.object_name = 'action_btn'
        self.action_btn.text = 'Activer'
        self.action_btn.checkable = True
        self.geometry = QRect(x=100, y=100, width=400, height=300)
        self.window_title = "SyntaxNode - Test d'intégration"
        main_layout = QVBoxLayout()
        self.set_layout(main_layout)
        main_layout.add_widget(self.title_label)
        main_layout.add_widget(self.separator_frame)
        main_layout.add_widget(self.counter_label)
        main_layout.add_widget(self.action_btn)
        self.action_btn.toggled.connect(self.on_action_toggled)

    def on_action_toggled(self, checked):
        self.is_active = checked
        self.click_count += 1
        self.counter_label.text = f'Clics : {self.click_count} - Actif : {self.is_active}'
        self.action_btn.text = 'Désactiver' if self.is_active else 'Activer'

def main():
    app = QApplication(sys.argv)
    w = IntegrationApp()
    w.show()
    sys.exit(app.exec())
if __name__ == '__main__':
    main()