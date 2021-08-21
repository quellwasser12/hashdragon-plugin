from .base_event_dialog import BaseEventDialog
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


# Class that handles the Breed dialog.
class BreedDialog(BaseEventDialog):

    def __init__(self, hashdragon, parent):
        BaseEventDialog.__init__(self, hashdragon, 'Breed', parent)

    def build_layout(self, action):
        self.layout = QGridLayout()
        self.layout.setColumnStretch(1, 4)
        self.layout.setColumnStretch(2, 4)

        hibernatetolabel = QLabel("Breed with")

        self.layout.addWidget(hibernatetolabel, 0, 0)

        self.breed_with_cb = QComboBox()
        self.breed_with_cb.addItems(["aa", "bb"])

        # self.hibernate_to = PayToEdit(self.main_window)
        hibernatetolabel.setBuddy(self.breed_with_cb)
        self.layout.addWidget(self.breed_with_cb, 0, 1)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
        self.result = None

    def create_opreturn(self, args):
        event = args['event']
        dest_address = args['dest_address']
        return event.build_hashdragon_op_return('breed', 0, 1, dest_address)
