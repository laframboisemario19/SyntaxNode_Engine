import sys
from PySide6.QtWidgets import QSpinBox, QGroupBox, QVBoxLayout, QLineEdit, QPushButton, QWidget, QApplication, QProgressBar
from PySide6.QtCore import QSize, QMargins
from __feature__ import snake_case, true_property #type: ignore[import-not-found]

class IntegrationApp(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.name_edit = QLineEdit()
        self.name_edit.object_name = 'name_edit'
        self.name_edit.placeholder_text = 'Nom du héros...'
        self.str_spin = QSpinBox()
        self.str_spin.object_name = 'str_spin'
        self.str_spin.suffix = ' pts'
        self.str_spin.prefix = 'Force : '
        self.str_spin.maximum = 15
        self.str_spin.value = 5
        self.agi_spin = QSpinBox()
        self.agi_spin.object_name = 'agi_spin'
        self.agi_spin.suffix = ' pts'
        self.agi_spin.prefix = 'Agilité : '
        self.agi_spin.maximum = 15
        self.agi_spin.value = 5
        self.total_progress = QProgressBar()
        self.total_progress.object_name = 'total_progress'
        self.total_progress.maximum = 20
        self.total_progress.value = 10
        self.total_progress.format = '%v / %m pts dépensés'
        self.save_btn = QPushButton()
        self.save_btn.object_name = 'save_btn'
        self.save_btn.text = 'Valider le personnage'
        self.object_name = 'app'
        self.size = QSize(width=1000, height=520)
        self.window_title = 'Créateur de Héros RPG'
        self.style_sheet = "QWidget { background-color: #1e1e1e; color: #d4af37; font-family: 'Segoe UI', sans-serif; font-size: 14px; } QGroupBox { border: 2px solid #3a3a3a; border-radius: 6px; margin-top: 15px; font-weight: bold; } QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 8px; color: #e6c555; } QLineEdit, QSpinBox { background-color: #2d2d2d; border: 1px solid #d4af37; border-radius: 4px; padding: 6px; color: #ffffff; } QSpinBox::up-button, QSpinBox::down-button { width: 20px; background-color: #3a3a3a; } QProgressBar { border: 2px solid #3a3a3a; border-radius: 6px; text-align: center; color: #1e1e1e; font-weight: bold; background-color: #2d2d2d; } QProgressBar::chunk { background-color: #d4af37; border-radius: 4px; } QPushButton { background-color: #d4af37; color: #1e1e1e; font-weight: bold; border-radius: 6px; padding: 12px; } QPushButton:hover { background-color: #e6c555; } QPushButton:pressed { background-color: #b5952f; }"
        main_layout = QVBoxLayout()
        self.set_layout(main_layout)
        identity_group = QGroupBox()
        main_layout.add_widget(identity_group)
        identity_layout = QVBoxLayout()
        identity_group.set_layout(identity_layout)
        identity_layout.add_widget(self.name_edit)
        stats_group = QGroupBox()
        main_layout.add_widget(stats_group)
        stats_layout = QVBoxLayout()
        stats_group.set_layout(stats_layout)
        stats_layout.add_widget(self.str_spin)
        stats_layout.add_widget(self.agi_spin)
        progress_group = QGroupBox()
        main_layout.add_widget(progress_group)
        progress_layout = QVBoxLayout()
        progress_group.set_layout(progress_layout)
        progress_layout.add_widget(self.total_progress)
        main_layout.add_widget(self.save_btn)
        self.str_spin.valueChanged.connect(self.on_stats_changed)
        self.agi_spin.valueChanged.connect(self.on_stats_changed)
        self.save_btn.clicked.connect(self.save_character)

    def save_character(self):
        nom = self.name_edit.text if self.name_edit.text else 'Héros Anonyme'
        self.window_title = f'{nom} - Validé !'

    def on_stats_changed(self, value):
        total = self.str_spin.value + self.agi_spin.value
        self.total_progress.value = total
        if total > 20:
            self.total_progress.format = 'Limite dépassée !'
            self.total_progress.style_sheet = 'QProgressBar::chunk { background-color: #cf3a3a; }'
        else:
            self.total_progress.format = '%v / %m pts dépensés'
            self.total_progress.style_sheet = 'QProgressBar::chunk { background-color: #d4af37; }'

def main():
    app = QApplication(sys.argv)
    w = IntegrationApp()
    w.show()
    sys.exit(app.exec())
if __name__ == '__main__':
    main()