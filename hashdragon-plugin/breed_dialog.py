from .base_event_dialog import BaseEventDialog
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from electroncash.bitcoin import TYPE_ADDRESS, TYPE_SCRIPT

from .event import Event
from .transactions import *
from .utils import *
from .hashdragons import Hashdragon


# Class that handles the Breed dialog.
class BreedDialog(BaseEventDialog):

    def __init__(self, hashdragon, parent, db):
        list_hashdragons = db.list_hashdragons()
        list_hashdragons.remove(hashdragon.hashdragon())
        self.hashdragons = list_hashdragons
        BaseEventDialog.__init__(self, hashdragon, 'Breed', parent, db)

    def build_layout(self, action):
        self.layout = QGridLayout()
        self.layout.setColumnStretch(1, 4)
        self.layout.setColumnStretch(2, 4)
        self.layout.setColumnStretch(3, 4)

        self.layout.addWidget(QLabel("Breed"), 0, 0)
        self.layout.addWidget(QLabel(self.hashdragon.hashdragon()), 0, 1)
        self.layout.addWidget(QLabel("Maturity: %s" % self.hashdragon.maturity()), 0, 2)

        breedwithlabel = QLabel("with")

        self.layout.addWidget(breedwithlabel, 1, 0)

        self.breed_with_cb = QComboBox()
        self.breed_with_cb.addItems(self.hashdragons)

        def on_combobox_changed(val):
            hd = Hashdragon.from_hex_string(val)
            self.maturity_label.setText("Maturity: %s" % hd.maturity())

        # self.hibernate_to = PayToEdit(self.main_window)
        breedwithlabel.setBuddy(self.breed_with_cb)
        self.layout.addWidget(self.breed_with_cb, 1, 1)
        self.breed_with_cb.currentTextChanged.connect(on_combobox_changed)

        self.maturity_label = QLabel("Maturity: %s" %
                                     Hashdragon.from_hex_string(self.breed_with_cb.currentText()).maturity())
        self.layout.addWidget(self.maturity_label, 1, 2)

        sendhatchlingtolabel = QLabel("Send Spawn to")

        self.layout.addWidget(sendhatchlingtolabel, 2, 0)

        self.send_hatchling_to = QLineEdit()
        # self.hibernate_to = PayToEdit(self.main_window)
        sendhatchlingtolabel.setBuddy(self.send_hatchling_to)
        self.layout.addWidget(self.send_hatchling_to, 2, 1)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
        self.result = None

    def create_opreturn(self, args):
        event = args['event']
        dest_address = args['dest_address']

        return event.build_hashdragon_op_return('breed', 1, 2, dest_address, 2, 3, 4)

    def create_event_txn(self):
        coins = self.main_window.wallet.get_spendable_coins(None, self.main_window.config)
        fee = None

        # Current location of the hashdragon, i.e. last valid tx for this hashdragon
        current_txn_ref1 = self.db.get_hashdragon_by_hash(self.hashdragon.hashdragon()).get_current_tx()
        output_index1 = self.db.get_hashdragon_by_hash(self.hashdragon.hashdragon()).get_current_index()

        current_txn_ref2 = self.db.get_hashdragon_by_hash(self.breed_with_cb.currentText()).get_current_tx()
        output_index2 = self.db.get_hashdragon_by_hash(self.breed_with_cb.currentText()).get_current_index()

        hashdragon_coin1 = None
        hashdragon_coin2 = None
        inputs = []

        for coin in coins:
            if coin['prevout_hash'] == current_txn_ref1 and coin['prevout_n'] == output_index1:
                hashdragon_coin1 = coin
            if coin['prevout_hash'] == current_txn_ref2 and coin['prevout_n'] == output_index2:
                hashdragon_coin2 = coin

        # TODO Add some logic for maturity.

        # Find a spendable coin that is not a hashdragon, and with sufficient value.
        spendable_coins = []
        for coin in coins:
            tx = self.main_window.wallet.transactions.get(coin['prevout_hash'])
            idx = -1
            flag = False
            vout_index = None
            for vout in tx.get_outputs():
                d, index = vout
                vout_index = coin['prevout_n']
                flag = self.main_window.wallet.is_mine(d)

                if isinstance(d, ScriptOutput) and d.is_opreturn():
                    script = d.to_script()
                    ops = Script.get_ops(script)
                    i, lokad = ops[1]

                    if lokad == unhexlify('d101d400'):
                        _, dest_index = ops[4]
                        idx = index_to_int(dest_index)

            if flag and (idx <= -1 or idx != vout_index) and coin['value'] > 400:
                spendable_coins.append(coin)

        if len(spendable_coins) <= 0:
            self.main_window.show_error("Not enough coins for transfer.")
            return False

        inputs.append(spendable_coins[0])

        # Outputs
        # Destination address
        # TODO Support multiple destination addresses, one for each hashdragon.
        dest_address = self.send_hatchling_to.text() if self.send_hatchling_to.text() != '' else None
        if dest_address is None:
            self.main_window.show_message("Invalid destination address.")
            return False

        outputs = []
        event = Event()

        args = {'event': event, 'dest_address': dest_address}

        op_return_script = self.create_opreturn(args)
        outputs.append((TYPE_SCRIPT, op_return_script, 0))

        addr = self.parse_address(dest_address)
        outputs.append((TYPE_ADDRESS, addr, 546)) # min required dust is 546 sat
        outputs.append((TYPE_ADDRESS, addr, 546)) # min required dust is 546 sat
        outputs.append((TYPE_ADDRESS, addr, 546)) # min required dust is 546 sat

        # TODO: Add option on UI to select a unique address for all 3, or 3 separate addresses.

        # Use value of hashdragon input as fee.
        # Fee will be added later when solving disappearing input coin issue
        tx = make_unsigned_transaction(self.main_window.wallet,
                                                inputs,
                                                outputs,
                                                self.main_window.config,
                                                mandatory_coins=[hashdragon_coin1, hashdragon_coin2])

        run_hook('sign_tx', self.main_window.wallet, tx)

        self.main_window.wallet.sign_transaction(tx, None)
        self.result = QDialog.Accepted

        # TODO Add a setting to enable this
        ## Uncomment this to show transaction in popup for debug.
        self.main_window.show_transaction(tx, None)

        def delayed_run_hook(wallet):
            # Delay running the hook to ensure the state has been successfully updated
            import time
            time.sleep(0.5)
            run_hook('update', wallet)

        def broadcast_done(success):
            if success:
                self.show_message('Hashdragon request %s has been successfully submitted.' % self.action)
                self.main_window.update_wallet()
                do_in_main_thread(delayed_run_hook, self.main_window.wallet)
            else:
                self.show_error('Error requesting hashdragon to %s.\n' % self.action)

            self.close()

        # self.main_window.network.broadcast_transaction(tx, callback=broadcast_done)

        return True
