import sys
from PySide6.QtWidgets import QLineEdit, QApplication, QLabel, QCheckBox, QWidget, QGroupBox, QProgressBar, QVBoxLayout
from PySide6.QtCore import QMargins, QRect
from __feature__ import snake_case, true_property #type: ignore[import-not-found]

class PasswordApp(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.password_input = QLineEdit()
        self.password_input.object_name = 'password_input'
        self.password_input.minimum_height = 44
        self.password_input.max_length = 32
        self.password_input.echo_mode = QLineEdit.EchoMode.Password
        self.password_input.placeholder_text = 'Entrez votre mot de passe...'
        self.strength_bar = QProgressBar()
        self.strength_bar.object_name = 'strength_bar'
        self.strength_bar.minimum_height = 16
        self.strength_bar.value = 0
        self.strength_bar.text_visible = False
        self.verdict_label = QLabel()
        self.verdict_label.object_name = 'verdict_label'
        self.verdict_label.minimum_height = 36
        self.verdict_label.text = 'Entrez un mot de passe'
        self.counter_label = QLabel()
        self.counter_label.object_name = 'counter_label'
        self.counter_label.text = '0 caracteres'
        self.check_length = QCheckBox()
        self.check_length.object_name = 'check_length'
        self.check_length.enabled = False
        self.check_length.text = 'Au moins 8 caracteres'
        self.check_upper = QCheckBox()
        self.check_upper.object_name = 'check_upper'
        self.check_upper.enabled = False
        self.check_upper.text = 'Une lettre majuscule'
        self.check_digit = QCheckBox()
        self.check_digit.object_name = 'check_digit'
        self.check_digit.enabled = False
        self.check_digit.text = 'Un chiffre'
        self.check_special = QCheckBox()
        self.check_special.object_name = 'check_special'
        self.check_special.enabled = False
        self.check_special.text = 'Un caractere special (!@#$...)'
        self.object_name = 'app'
        self.geometry = QRect(x=350, y=150, width=440, height=520)
        self.window_title = 'Validateur de mot de passe'
        self.style_sheet = 'QWidget { background-color: #0a0a0a; color: #00ff88; font-family: Consolas; font-size: 13px; } QGroupBox { border: 1px solid #00ff88; border-radius: 8px; margin-top: 14px; padding-top: 10px; color: #00ff88; font-weight: bold; } QGroupBox::title { subcontrol-origin: margin; left: 12px; } QLineEdit { background-color: #111111; border: 2px solid #00ff88; border-radius: 6px; padding: 8px 12px; color: #00ff88; font-size: 16px; letter-spacing: 2px; } QLineEdit:focus { border: 2px solid #00ffcc; } QCheckBox { color: #00ff88; spacing: 8px; font-size: 12px; } QCheckBox::indicator { width: 16px; height: 16px; border: 1px solid #00ff88; border-radius: 3px; background-color: #111111; } QCheckBox::indicator:checked { background-color: #00ff88; } QProgressBar { background-color: #111111; border: 1px solid #00ff88; border-radius: 4px; height: 12px; text-align: center; } QProgressBar::chunk { border-radius: 4px; background-color: #00ff88; } QPushButton { background-color: #00ff88; color: #0a0a0a; font-weight: bold; border-radius: 6px; padding: 8px 16px; font-family: Consolas; } QPushButton:hover { background-color: #00ffcc; } QLabel#verdict_label { font-size: 18px; font-weight: bold; } QLabel#counter_label { color: #446644; font-size: 11px; }'
        main_layout = QVBoxLayout()
        self.set_layout(main_layout)
        input_group = QGroupBox()
        main_layout.add_widget(input_group)
        input_layout = QVBoxLayout()
        input_group.set_layout(input_layout)
        input_layout.add_widget(self.password_input)
        strength_group = QGroupBox()
        main_layout.add_widget(strength_group)
        strength_layout = QVBoxLayout()
        strength_group.set_layout(strength_layout)
        strength_layout.add_widget(self.verdict_label)
        strength_layout.add_widget(self.strength_bar)
        criteria_group = QGroupBox()
        main_layout.add_widget(criteria_group)
        criteria_layout = QVBoxLayout()
        criteria_group.set_layout(criteria_layout)
        criteria_layout.add_widget(self.check_length)
        criteria_layout.add_widget(self.check_upper)
        criteria_layout.add_widget(self.check_digit)
        criteria_layout.add_widget(self.check_special)
        main_layout.add_widget(self.counter_label)
        self.password_input.textChanged.connect(self.on_text_changed)

    def on_text_changed(self, text):
        n = len(text)
        self.counter_label.text = f'{n} caracteres'
        c = None
        has_upper = any((c.isupper() for c in text))
        has_digit = any((c.isdigit() for c in text))
        has_special = any((c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in text))
        has_length = n >= 8
        self.check_length.checked = has_length
        self.check_upper.checked = has_upper
        self.check_digit.checked = has_digit
        self.check_special.checked = has_special
        score = sum([has_length, has_upper, has_digit, has_special])
        self.strength_bar.value = score * 25
        if score == 0:
            self.verdict_label.text = 'Entrez un mot de passe'
            self.verdict_label.style_sheet = 'color: #446644; font-size: 18px; font-weight: bold;'
        elif score == 1:
            self.verdict_label.text = 'Tres faible'
            self.verdict_label.style_sheet = 'color: #ff4444; font-size: 18px; font-weight: bold;'
        elif score == 2:
            self.verdict_label.text = 'Faible'
            self.verdict_label.style_sheet = 'color: #ff8800; font-size: 18px; font-weight: bold;'
        elif score == 3:
            self.verdict_label.text = 'Bon'
            self.verdict_label.style_sheet = 'color: #ffff00; font-size: 18px; font-weight: bold;'
        else:
            self.verdict_label.text = 'Excellent !'
            self.verdict_label.style_sheet = 'color: #00ff88; font-size: 18px; font-weight: bold;'

def main():
    app = QApplication(sys.argv)
    w = PasswordApp()
    w.show()
    sys.exit(app.exec())
if __name__ == '__main__':
    main()