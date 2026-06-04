import sys
from PySide6.QtWidgets import QLabel, QVBoxLayout, QLineEdit, QPushButton, QHBoxLayout, QWidget, QCheckBox, QSlider, QApplication
from PySide6.QtCore import Qt, QRect, QMargins
from __feature__ import snake_case, true_property #type: ignore[import-not-found]

class PlayerProfil(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.name_input = QLineEdit()
        self.name_input.object_name = 'name_input'
        self.name_input.text = 'Chat désactivé...'
        self.name_input.max_length = 20
        self.volume_slider = QSlider()
        self.volume_slider.object_name = 'volume_slider'
        self.volume_slider.enabled = False
        self.volume_slider.maximum = 100
        self.volume_slider.value = 50
        self.volume_slider.orientation = Qt.Orientation.Horizontal
        self.advanced_cb = QCheckBox()
        self.advanced_cb.object_name = 'advanced_cb'
        self.advanced_cb.text = 'Activer le chat vocal'
        self.submit_btn = QPushButton()
        self.submit_btn.object_name = 'submit_btn'
        self.submit_btn.text = 'Sauvegarder'
        self.status_label = QLabel()
        self.status_label.object_name = 'status_label'
        self.status_label.text = 'En attente de sauvegarde...'
        self.status_label.alignment = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
        self.object_name = 'app'
        self.geometry = QRect(x=100, y=100, width=450, height=300)
        self.window_title = 'Configuration du Profil'
        main_layout = QVBoxLayout()
        self.set_layout(main_layout)
        form_layout = QHBoxLayout()
        main_layout.add_layout(form_layout)
        name_label = QLabel()
        form_layout.add_widget(name_label)
        form_layout.add_widget(self.name_input)
        main_layout.add_widget(self.advanced_cb)
        main_layout.add_widget(self.volume_slider)
        main_layout.add_widget(self.submit_btn)
        main_layout.add_widget(self.status_label)
        self.submit_btn.clicked.connect(self.on_submit_clicked)
        self.advanced_cb.toggled.connect(self.on_advanced_toggled)

    def on_advanced_toggled(self, checked):
        self.volume_slider.enabled = checked
        if checked:
            self.name_input.placeholder_text = 'Chat activé, entrez un pseudo...'
        else:
            self.name_input.placeholder_text = 'Chat désactivé...'

    def on_submit_clicked(self, checked):
        pseudo = self.name_input.text if self.name_input.text else 'Anonyme'
        vol = self.volume_slider.value if self.volume_slider.enabled else 'N/A'
        self.status_label.text = f'Profil sauvegardé : {pseudo} (Volume : {vol})'

def main():
    app = QApplication(sys.argv)
    w = PlayerProfil()
    w.show()
    sys.exit(app.exec())
if __name__ == '__main__':
    main()