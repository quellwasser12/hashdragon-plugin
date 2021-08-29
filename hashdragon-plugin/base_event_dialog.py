import time

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from electroncash import Transaction
from electroncash.util import PrintError, do_in_main_thread
from electroncash.address import Address, ScriptOutput, Script
from electroncash.bitcoin import TYPE_ADDRESS, TYPE_SCRIPT
from electroncash_gui.qt.paytoedit import PayToEdit
from electroncash_gui.qt.util import MessageBoxMixin

from binascii import unhexlify

from .event import Event
from .transactions import *
from .utils import index_to_int


class BaseEventDialog(QDialog, MessageBoxMixin, PrintError):

    def __init__(self, hashdragon, action, parent, db):
        QDialog.__init__(self, parent)
        self.main_window = parent
        self.hashdragon = hashdragon
        self.action = action
        self.db = db

        self.setMinimumWidth(750)
        self.setWindowTitle(action)

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.create_event_txn)
        self.buttonBox.rejected.connect(self.reject)

        self.build_layout(action)

    def build_layout(self, action):
        self.layout = QGridLayout()
        self.layout.setColumnStretch(1, 4)
        self.layout.setColumnStretch(2, 4)

        hibernatetolabel = QLabel("%s to" % action)

        self.layout.addWidget(hibernatetolabel, 0, 0)

        self.hibernate_to = QLineEdit()
        # self.hibernate_to = PayToEdit(self.main_window)
        hibernatetolabel.setBuddy(self.hibernate_to)
        self.layout.addWidget(self.hibernate_to, 0, 1)

        # self.completions = QStringListModel()
        # completer = QCompleter(self.hibernate_to)
        # completer.setCaseSensitivity(False)
        # self.hibernate_to.setCompleter(completer)
        # completer.setModel(self.completions)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
        self.result = None

    @staticmethod
    def parse_address(address):
        return Address.from_string(address)

    def create_opreturn(self, args):
        pass # to be implemented by subclasses

    def create_event_txn(self):
        coins = self.main_window.wallet.get_spendable_coins(None, self.main_window.config)
        fee = None

        # Current location of the hashdragon, i.e. last valid tx for this hashdragon
        current_txn_ref = self.db.get_hashdragon_by_hash(self.hashdragon.hashdragon()).get_current_tx()
        ok, r = self.main_window.wallet.network.get_raw_tx_for_txid(current_txn_ref, timeout=10.0)

        output_index = -1

        if not ok:
            self.main_window.show_error("Cannot retrieve original hashdragon transaction.")
            return False
        else:
            tx = Transaction(r, sign_schnorr=self.main_window.wallet.is_schnorr_enabled())
            for vout in tx.get_outputs():
                d, index = vout
                if isinstance(d, ScriptOutput) and d.is_opreturn():
                    script = d.to_script()
                    ops = Script.get_ops(script)
                    i, lokad = ops[1]

                    if lokad == unhexlify('d101d400'):
                        _, o = ops[4]
                        output_index = index_to_int(o)

        inputs = []
        hashdragon_coin = None

        # First input is the vout of the previous valid tx
        for coin in coins:
            if coin['prevout_hash'] == current_txn_ref and coin['prevout_n'] == output_index:
                hashdragon_coin = coin

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

        dest_address = self.hibernate_to.text() if self.hibernate_to.text() != '' else None
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

        # Use value of hashdragon input as fee.
        # Fee will be added later when solving disappearing input coin issue
        tx = make_unsigned_transaction(self.main_window.wallet,
                                                inputs,
                                                outputs,
                                                self.main_window.config,
                                                mandatory_coins=[hashdragon_coin])

        run_hook('sign_tx', self.main_window.wallet, tx)

        self.main_window.wallet.sign_transaction(tx, None)
        self.result = QDialog.Accepted

        # TODO Add a setting to enable this
        ## Uncomment this to show transaction in popup for debug.
        #self.main_window.show_transaction(tx, None)

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

        self.main_window.network.broadcast_transaction(tx, callback=broadcast_done)

        return True
