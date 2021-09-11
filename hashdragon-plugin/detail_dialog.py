from PyQt5.QtWidgets import *

from electroncash.util import PrintError
from .hashdragons import HashdragonDescriber


class DetailDialog(QDialog, PrintError):

    def __init__(self, hashdragon, parent, db):
        QDialog.__init__(self, parent)
        self.db = db

        self.setMinimumWidth(750)
        self.setWindowTitle("Hashdragon")

        describer = HashdragonDescriber()
        db_entry = db.get_hashdragon_by_hash(hashdragon.hashdragon())

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QGridLayout()
        self.layout.setColumnStretch(1, 4)
        self.layout.setColumnStretch(2, 4)

        row = 0
        message = QLabel("Hashdragon")
        self.layout.addWidget(message, row, 0)

        self.hash_label = QLabel(hashdragon.hashdragon())
        self.layout.addWidget(self.hash_label, row, 1)

        row += 1
        description = QLabel(describer.describe(hashdragon))
        self.layout.addWidget(description, row, 0, 1, 2)

        row += 1
        self.layout.addWidget(QLabel('Hatched Block: '), row, 0)
        self.layout.addWidget(QLabel(f'{db_entry.get_hatched_block()}'), row, 1)

        row += 1
        self.layout.addWidget(QLabel('Strength: '), row, 0)
        self.strength = hashdragon.strength()
        self.layout.addWidget(QLabel(f'{self.strength}'), row, 1)

        row += 1
        self.layout.addWidget(QLabel('Inner Light: '), row, 0)
        self.inner_light = hashdragon.inner_light()
        inner_light_value = round(self.inner_light * 100.0 / 200.0, 1)
        self.layout.addWidget(QLabel(f'{inner_light_value}%'), row, 1)

        row += 1
        self.layout.addWidget(QLabel('Presence: '), row, 0)
        self.presence = hashdragon.presence()
        presence_value = round(self.presence * 100.0 / 200.0, 1)
        self.layout.addWidget(QLabel(f'{presence_value}%'), row, 1)

        row += 1
        self.layout.addWidget(QLabel('Charm: '), row, 0)
        self.charm = hashdragon.charm()
        charm_value = round(self.charm * 100.0 / 200.0, 1)
        self.layout.addWidget(QLabel(f'{charm_value}%'), row, 1)

        row += 1
        self.layout.addWidget(QLabel('Strangeness: '), row, 0)
        self.strangeness = hashdragon.strangeness()
        strangeness_value = round(self.strangeness * 100.0 / 200.0, 1)
        self.layout.addWidget(QLabel(f'{strangeness_value}%'), row, 1)

        row += 1
        self.layout.addWidget(QLabel('Beauty: '), row, 0)
        self.beauty = hashdragon.beauty()
        beauty_value = round(self.beauty * 100.0 / 200.0, 1)
        self.layout.addWidget(QLabel(f'{beauty_value}%'), row, 1)

        row += 1
        self.layout.addWidget(QLabel('Truth: '), row, 0)
        self.truth = hashdragon.truth()
        truth_value = round(self.truth * 100.0 / 200.0, 1)
        self.layout.addWidget(QLabel(f'{truth_value}%'), row, 1)

        row += 1
        self.layout.addWidget(QLabel('Magic: '), row, 0)
        self.magic = hashdragon.magic()
        magic_value = round(self.magic * 100.0 / 200.0, 1)
        self.layout.addWidget(QLabel(f'{magic_value}%'), row, 1)

        row += 1
        self.layout.addWidget(QLabel('Special Powers: '), row, 0)
        self.special_powers = hashdragon.special_powers()
        self.layout.addWidget(QLabel(f'{self.special_powers}'), row, 1)

        row += 1
        self.layout.addWidget(QLabel('Manifestation: '), row, 0)
        self.manifestation = hashdragon.manifestation()
        self.layout.addWidget(QLabel(f'{self.manifestation}'), row, 1)

        row += 1
        self.layout.addWidget(QLabel('Arcana: '), row, 0)
        self.arcana = hashdragon.arcana()
        self.layout.addWidget(QLabel(f'{self.arcana}'), row, 1)

        row += 1
        self.layout.addWidget(QLabel('Cabala: '), row, 0)
        self.cabala = hashdragon.cabala()
        self.layout.addWidget(QLabel(f'{self.cabala}'), row, 1)

        row += 1
        self.layout.addWidget(QLabel('Maturity: '), row, 0)
        self.maturity = hashdragon.maturity()
        self.layout.addWidget(QLabel(f'{self.maturity} (can breed after block {self.maturity + db_entry.get_hatched_block()})'), row, 1)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
