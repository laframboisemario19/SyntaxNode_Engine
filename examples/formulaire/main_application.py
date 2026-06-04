import sys
from PySide6.QtWidgets import QLineEdit, QRadioButton, QApplication, QLabel, QHBoxLayout, QWidget, QGroupBox, QPushButton, QVBoxLayout, QTextEdit
from PySide6.QtCore import Qt, QMargins, QRect
from __feature__ import snake_case, true_property #type: ignore[import-not-found]

class ContactFormApp(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.first_name_input = QLineEdit()
        self.first_name_input.object_name = 'first_name_input'
        self.first_name_input.max_length = 50
        self.first_name_input.placeholder_text = 'Votre prénom...'
        self.last_name_input = QLineEdit()
        self.last_name_input.object_name = 'last_name_input'
        self.last_name_input.max_length = 50
        self.last_name_input.placeholder_text = 'Votre nom de famille...'
        self.email_input = QLineEdit()
        self.email_input.object_name = 'email_input'
        self.email_input.max_length = 120
        self.email_input.placeholder_text = 'exemple@courriel.com'
        self.subject_input = QLineEdit()
        self.subject_input.object_name = 'subject_input'
        self.subject_input.max_length = 100
        self.subject_input.placeholder_text = 'Résumez votre demande en quelques mots...'
        self.message_input = QTextEdit()
        self.message_input.object_name = 'message_input'
        self.message_input.minimum_height = 120
        self.message_input.placeholder_text = 'Décrivez votre demande en détail...'
        self.radio_standard = QRadioButton()
        self.radio_standard.object_name = 'radio_standard'
        self.radio_standard.text = 'Standard'
        self.radio_standard.checked = True
        self.radio_urgent = QRadioButton()
        self.radio_urgent.object_name = 'radio_urgent'
        self.radio_urgent.style_sheet = 'QRadioButton:checked { color: #f38ba8; } QRadioButton::indicator:checked { background-color: #f38ba8; border: 2px solid #f38ba8; border-radius: 5px; }'
        self.radio_urgent.text = 'Urgent'
        self.submit_btn = QPushButton()
        self.submit_btn.object_name = 'submit_btn'
        self.submit_btn.minimum_height = 40
        self.submit_btn.text = 'Envoyer le message'
        self.radio_feedback = QRadioButton()
        self.radio_feedback.object_name = 'radio_feedback'
        self.radio_feedback.style_sheet = 'QRadioButton:checked { color: #a6e3a1; } QRadioButton::indicator:checked { background-color: #a6e3a1; border: 2px solid #a6e3a1; border-radius: 5px; }'
        self.radio_feedback.text = 'Rétroaction'
        self.confirm_label = QLabel()
        self.confirm_label.object_name = 'confirm_label'
        self.confirm_label.visible = False
        self.confirm_label.style_sheet = 'background-color: #1e3a2f; color: #a6e3a1; border: 1px solid #a6e3a1; border-radius: 6px; padding: 12px; font-size: 13px;'
        self.confirm_label.alignment = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
        self.object_name = 'app'
        self.geometry = QRect(x=100, y=100, width=520, height=680)
        self.window_title = 'Formulaire de contact'
        self.style_sheet = 'QWidget { background-color: #1e1e2e; color: #cdd6f4; font-family: Segoe UI; } QLabel { color: #cdd6f4; } QLineEdit, QTextEdit { background-color: #313244; border: 1px solid #45475a; border-radius: 6px; padding: 6px; color: #cdd6f4; } QLineEdit:focus, QTextEdit:focus { border: 1px solid #89b4fa; } QPushButton { background-color: #89b4fa; color: #1e1e2e; font-weight: bold; border-radius: 6px; padding: 8px 16px; } QPushButton:hover { background-color: #b4befe; } QGroupBox { border: 1px solid #45475a; border-radius: 6px; margin-top: 10px; padding-top: 8px; color: #a6adc8; font-weight: bold; } QGroupBox::title { subcontrol-origin: margin; left: 10px; } QRadioButton { color: #cdd6f4; spacing: 8px; } QRadioButton::indicator:checked { background-color: #89b4fa; border: 2px solid #89b4fa; border-radius: 5px; }'
        main_layout = QVBoxLayout()
        self.set_layout(main_layout)
        title_label = QLabel()
        main_layout.add_widget(title_label)
        identity_group = QGroupBox()
        main_layout.add_widget(identity_group)
        identity_layout = QVBoxLayout()
        identity_group.set_layout(identity_layout)
        name_row = QHBoxLayout()
        identity_layout.add_layout(name_row)
        first_name_label = QLabel()
        name_row.add_widget(first_name_label)
        name_row.add_widget(self.first_name_input)
        last_name_label = QLabel()
        name_row.add_widget(last_name_label)
        name_row.add_widget(self.last_name_input)
        email_row = QHBoxLayout()
        identity_layout.add_layout(email_row)
        email_label = QLabel()
        email_row.add_widget(email_label)
        email_row.add_widget(self.email_input)
        n_13 = QGroupBox()
        main_layout.add_widget(n_13)
        subject_layout = QVBoxLayout()
        n_13.set_layout(subject_layout)
        subject_label = QLabel()
        subject_layout.add_widget(subject_label)
        subject_layout.add_widget(self.subject_input)
        proprity_group = QGroupBox()
        main_layout.add_widget(proprity_group)
        priority_layout = QHBoxLayout()
        proprity_group.set_layout(priority_layout)
        priority_layout.add_widget(self.radio_standard)
        priority_layout.add_widget(self.radio_urgent)
        priority_layout.add_widget(self.radio_feedback)
        message_group = QGroupBox()
        main_layout.add_widget(message_group)
        message_layout = QVBoxLayout()
        message_group.set_layout(message_layout)
        message_layout.add_widget(self.message_input)
        main_layout.add_widget(self.submit_btn)
        main_layout.add_widget(self.confirm_label)
        self.submit_btn.clicked.connect(self.on_submit_clicked)

    def on_submit_clicked(self):
        prenom = self.first_name_input.text if self.first_name_input.text else 'Non renseigné'
        nom = self.last_name_input.text if self.last_name_input.text else 'Non renseigné'
        courriel = self.email_input.text if self.email_input.text else 'Non renseigné'
        sujet = self.subject_input.text if self.subject_input.text else 'Sans sujet'
        if self.radio_urgent.checked:
            priorite = 'Urgent'
        elif self.radio_feedback.checked:
            priorite = 'Rétroaction'
        else:
            priorite = 'Standard'
        self.confirm_label.text = f'Message envoyé !\\n{prenom} {nom} — {courriel}\\nSujet : {sujet} [{priorite}]'
        self.confirm_label.visible = True

def main():
    app = QApplication(sys.argv)
    w = ContactFormApp()
    w.show()
    sys.exit(app.exec())
if __name__ == '__main__':
    main()