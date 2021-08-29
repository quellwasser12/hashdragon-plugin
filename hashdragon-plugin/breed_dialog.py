from .base_event_dialog import BaseEventDialog
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .utils import *

# Class that handles the Breed dialog.
class BreedDialog(BaseEventDialog):

    def __init__(self, hashdragon, parent, db):
        self.db = db
        list_hashdragons = db.list_hashdragons()
        list_hashdragons.remove(hashdragon.hashdragon())
        self.hashdragons = list_hashdragons
        BaseEventDialog.__init__(self, hashdragon, 'Breed', parent)

    def build_layout(self, action):
        self.layout = QGridLayout()
        self.layout.setColumnStretch(1, 4)
        self.layout.setColumnStretch(2, 4)

        breedwithlabel = QLabel("Breed with")

        self.layout.addWidget(breedwithlabel, 0, 0)

        self.breed_with_cb = QComboBox()
        self.breed_with_cb.addItems(self.hashdragons)

        # self.hibernate_to = PayToEdit(self.main_window)
        breedwithlabel.setBuddy(self.breed_with_cb)
        self.layout.addWidget(self.breed_with_cb, 0, 1)

        sendhatchlingtolabel = QLabel("Send Spawn to")

        self.layout.addWidget(sendhatchlingtolabel, 1, 0)

        self.send_hatchling_to = QLineEdit()
        # self.hibernate_to = PayToEdit(self.main_window)
        sendhatchlingtolabel.setBuddy(self.send_hatchling_to)
        self.layout.addWidget(self.send_hatchling_to, 1, 1)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
        self.result = None

    def create_opreturn(self, args):
        event = args['event']
        dest_address = args['dest_address']
        return event.build_hashdragon_op_return('breed', 0, 1, dest_address)

    def create_event_txn(self):
        coins = self.main_window.wallet.get_spendable_coins(None, self.main_window.config)
        fee = None

        # Current location of the hashdragon, i.e. last valid tx for this hashdragon
        current_txn_ref = self.db.get_hashdragon_by_hash(self.hashdragon.hashdragon()).get_current_tx()
        ok, r = self.main_window.wallet.network.get_raw_tx_for_txid(current_txn_ref, timeout=10.0)

        output_index = -1


        tx = find_last_valid_tx_for_hashdragon(self.main_window.wallet, self.hashdragon.hashdragon(), self.main_window.config)

        print("Current hashdragon: %s" % self.hashdragon.hashdragon())
        print("Current txnref: %s" % current_txn_ref)
        if tx is not None:
            print("Found txnref: %s" % tx.txid())
        else:
            print("No txnref found.")
