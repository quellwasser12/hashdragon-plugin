from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from electroncash.util import PrintError

from .hashdragons import HashdragonDescriber

class WanderDialog(QDialog, PrintError):

    def __init__(self, hashdragon, parent):
        QDialog.__init__(self, parent)
        self.main_window = parent
        self.hashdragon = hashdragon

        self.setMinimumWidth(750)
        self.setWindowTitle("Wander")

        describer = HashdragonDescriber()

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.create_wander)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QGridLayout()
        self.layout.setColumnStretch(1, 4)
        self.layout.setColumnStretch(2, 4)

        self.layout.addWidget(QLabel("Wander to"), 0, 0)

        self.wander_to = QLineEdit()
        self.layout.addWidget(self.wander_to, 0, 1)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)



    def create_wander(self):
        coins = self.main_window.get_coins()
        fee = None

        for coin in coins:
            tx = self.main_window.wallet.transactions.get(coin['prevout_hash'])


        self.result = QDialog.Accepted
       # try:
       #     tx = self.main_window.wallet.make_unsigned_transaction(coins, outputs, self.main_window.config, fee, None, mandatory_coins=[baton_input])
