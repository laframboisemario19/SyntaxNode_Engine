import sys
from PySide6.QtWidgets import QApplication, QLabel, QSlider, QWidget, QGroupBox, QVBoxLayout
from PySide6.QtCore import Qt, QMargins, QRect
from __feature__ import snake_case, true_property #type: ignore[import-not-found]

class TacosApp(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.montant_slider = QSlider()
        self.montant_slider.object_name = 'montant_slider'
        self.montant_slider.minimum_height = 36
        self.montant_slider.minimum = 5
        self.montant_slider.maximum = 200
        self.montant_slider.single_step = 5
        self.montant_slider.value = 50
        self.montant_slider.orientation = Qt.Orientation.Horizontal
        self.pourcentage_slider = QSlider()
        self.pourcentage_slider.object_name = 'pourcentage_slider'
        self.pourcentage_slider.minimum_height = 36
        self.pourcentage_slider.maximum = 30
        self.pourcentage_slider.value = 15
        self.pourcentage_slider.orientation = Qt.Orientation.Horizontal
        self.montant_label = QLabel()
        self.montant_label.object_name = 'montant_label'
        self.montant_label.text = 'Facture : 50 $'
        self.pourcentage_label = QLabel()
        self.pourcentage_label.object_name = 'pourcentage_label'
        self.pourcentage_label.text = 'Pourboire : 15 %'
        self.pourboire_label = QLabel()
        self.pourboire_label.object_name = 'pourboire_label'
        self.pourboire_label.minimum_height = 44
        self.pourboire_label.text = '7.50 $'
        self.total_label = QLabel()
        self.total_label.object_name = 'total_label'
        self.total_label.minimum_height = 48
        self.total_label.text = 'Total : 57.50 $'
        self.emoji_label = QLabel()
        self.emoji_label.object_name = 'emoji_label'
        self.emoji_label.minimum_height = 44
        self.emoji_label.text = 'Merci beaucoup !'
        self.object_name = 'app'
        self.geometry = QRect(x=350, y=150, width=460, height=520)
        self.window_title = 'Taco Loco - Calculateur de pourboire'
        self.style_sheet = 'QWidget { background-color: #fff8e7; color: #3d2b00; font-family: Segoe UI; font-size: 13px; } QGroupBox { border: 2px solid #f4a226; border-radius: 10px; margin-top: 14px; padding-top: 10px; color: #c45c00; font-weight: bold; font-size: 13px; } QGroupBox::title { subcontrol-origin: margin; left: 12px; } QSlider::groove:horizontal { background: #f4d7a0; border-radius: 4px; height: 8px; } QSlider::handle:horizontal { background: #f4a226; border: 2px solid #c45c00; width: 20px; height: 20px; margin: -6px 0; border-radius: 10px; } QSlider::sub-page:horizontal { background: #f4a226; border-radius: 4px; } QLabel { background-color: transparent; border: none; } QLabel#pourboire_label { background-color: #fde68a; border: 2px solid #f4a226; border-radius: 8px; padding: 8px; font-size: 20px; font-weight: bold; color: #c45c00; } QLabel#total_label { background-color: #f4a226; border: 2px solid #c45c00; border-radius: 8px; padding: 8px; font-size: 22px; font-weight: bold; color: #fff8e7; } QLabel#emoji_label { font-size: 32px; background-color: transparent; border: none; }'
        main_layout = QVBoxLayout()
        self.set_layout(main_layout)
        montant_group = QGroupBox()
        main_layout.add_widget(montant_group)
        montant_layout = QVBoxLayout()
        montant_group.set_layout(montant_layout)
        montant_layout.add_widget(self.montant_label)
        montant_layout.add_widget(self.montant_slider)
        pourcentage_group = QGroupBox()
        main_layout.add_widget(pourcentage_group)
        pourcentage_layout = QVBoxLayout()
        pourcentage_group.set_layout(pourcentage_layout)
        pourcentage_layout.add_widget(self.pourcentage_label)
        pourcentage_layout.add_widget(self.pourcentage_slider)
        resultat_group = QGroupBox()
        main_layout.add_widget(resultat_group)
        resultat_layout = QVBoxLayout()
        resultat_group.set_layout(resultat_layout)
        resultat_layout.add_widget(self.pourboire_label)
        resultat_layout.add_widget(self.total_label)
        main_layout.add_widget(self.emoji_label)
        self.montant_slider.valueChanged.connect(self.on_montant_changed)
        self.pourcentage_slider.valueChanged.connect(self.on_pourcentage_changed)

    def on_montant_changed(self, value):
        self.montant_label.text = f'Facture : {value} $'
        pourcentage = self.pourcentage_slider.value
        pourboire = value * pourcentage / 100
        total = value + pourboire
        self.pourboire_label.text = f'{pourboire:.2f} $'
        self.total_label.text = f'Total : {total:.2f} $'
        if pourcentage >= 25:
            self.emoji_label.text = 'Tres genereux !'
        elif pourcentage >= 15:
            self.emoji_label.text = 'Merci beaucoup !'
        elif pourcentage >= 10:
            self.emoji_label.text = 'Merci !'
        else:
            self.emoji_label.text = 'Hmm...'

    def on_pourcentage_changed(self, value):
        self.pourcentage_label.text = f'Pourboire : {value} %'
        montant = self.montant_slider.value
        pourboire = montant * value / 100
        total = montant + pourboire
        self.pourboire_label.text = f'{pourboire:.2f} $'
        self.total_label.text = f'Total : {total:.2f} $'
        if value >= 25:
            self.emoji_label.text = 'Tres genereux !'
        elif value >= 15:
            self.emoji_label.text = 'Merci beaucoup !'
        elif value >= 10:
            self.emoji_label.text = 'Merci !'
        else:
            self.emoji_label.text = 'Hmm...'

def main():
    app = QApplication(sys.argv)
    w = TacosApp()
    w.show()
    sys.exit(app.exec())
if __name__ == '__main__':
    main()