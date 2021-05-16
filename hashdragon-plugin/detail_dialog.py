from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from electroncash.util import PrintError

class DetailDialog(QDialog, PrintError):

    def __init__(self, hashdragon, parent):
        QDialog.__init__(self, parent)

        self.setMinimumWidth(750)
        self.setWindowTitle("Hashdragon")

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

        # TODO Add more details


        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
