from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from electroncash.util import PrintError

from .hashdragons import HashdragonDescriber


class DetailDialog(QDialog, PrintError):

    def __init__(self, hashdragon, parent):
        QDialog.__init__(self, parent)

        self.setMinimumWidth(750)
        self.setWindowTitle("Hashdragon")

        describer = HashdragonDescriber()

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QGridLayout()
        self.layout.setColumnStretch(1, 4)
        self.layout.setColumnStretch(2, 4)

        message = QLabel("Hashdragon")
        self.layout.addWidget(message, 0, 0)

        self.hash_label = QLabel(hashdragon.hashdragon())
        self.layout.addWidget(self.hash_label, 0, 1)

        description = QLabel(describer.describe(hashdragon))
        self.layout.addWidget(description, 1, 0, 1, 2)

        self.layout.addWidget(QLabel('Strength: '), 2, 0)
        self.strength = hashdragon.strength()
        self.layout.addWidget(QLabel(f'{self.strength}'), 2, 1)

        self.layout.addWidget(QLabel('Inner Light: '), 3, 0)
        self.inner_light = hashdragon.inner_light()
        inner_light_value = round(self.inner_light * 100.0 / 200.0, 1)
        self.layout.addWidget(QLabel(f'{inner_light_value}%'), 3, 1)

        self.layout.addWidget(QLabel('Presence: '), 4, 0)
        self.presence = hashdragon.presence()
        presence_value = round(self.presence * 100.0 / 200.0, 1)
        self.layout.addWidget(QLabel(f'{presence_value}%'), 4, 1)

        self.layout.addWidget(QLabel('Charm: '), 5, 0)
        self.charm = hashdragon.charm()
        charm_value = round(self.charm * 100.0 / 200.0, 1)
        self.layout.addWidget(QLabel(f'{charm_value}%'), 5, 1)

        self.layout.addWidget(QLabel('Strangeness: '), 6, 0)
        self.strangeness = hashdragon.strangeness()
        strangeness_value = round(self.strangeness * 100.0 / 200.0, 1)
        self.layout.addWidget(QLabel(f'{strangeness_value}%'), 6, 1)

        self.layout.addWidget(QLabel('Beauty: '), 7, 0)
        self.beauty = hashdragon.beauty()
        beauty_value = round(self.beauty * 100.0 / 200.0, 1)
        self.layout.addWidget(QLabel(f'{beauty_value}%'), 7, 1)

        self.layout.addWidget(QLabel('Truth: '), 8, 0)
        self.truth = hashdragon.truth()
        truth_value = round(self.truth * 100.0 / 200.0, 1)
        self.layout.addWidget(QLabel(f'{truth_value}%'), 8, 1)

        self.layout.addWidget(QLabel('Magic: '), 9, 0)
        self.magic = hashdragon.magic()
        magic_value = round(self.magic * 100.0 / 200.0, 1)
        self.layout.addWidget(QLabel(f'{magic_value}%'), 9, 1)

        self.layout.addWidget(QLabel('Special Powers: '), 10, 0)
        self.special_powers = hashdragon.special_powers()
        self.layout.addWidget(QLabel(f'{self.special_powers}'), 10, 1)

        self.layout.addWidget(QLabel('Manifestation: '), 11, 0)
        self.manifestation = hashdragon.manifestation()
        self.layout.addWidget(QLabel(f'{self.manifestation}'), 11, 1)

        self.layout.addWidget(QLabel('Arcana: '), 12, 0)
        self.arcana = hashdragon.arcana()
        self.layout.addWidget(QLabel(f'{self.arcana}'), 12, 1)

        self.layout.addWidget(QLabel('Cabala: '), 13, 0)
        self.cabala = hashdragon.cabala()
        self.layout.addWidget(QLabel(f'{self.cabala}'), 13, 1)

        self.layout.addWidget(QLabel('Maturity: '), 14, 0)
        self.maturity = hashdragon.maturity()
        self.layout.addWidget(QLabel(f'{self.maturity}'), 14, 1)

        self.layout.addWidget(QLabel('Sigil: '), 15, 0)
        self.sigil = hashdragon.sigil_unicode()
        self.layout.addWidget(QLabel(f'{self.sigil}'), 15, 1)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
