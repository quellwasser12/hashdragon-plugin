from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from electroncash import Transaction
from electroncash.util import PrintError
from electroncash.address import Address, ScriptOutput, Script
from electroncash.bitcoin import TYPE_ADDRESS, TYPE_SCRIPT
from electroncash_gui.qt.paytoedit import PayToEdit
from electroncash_gui.qt.util import MessageBoxMixin

from binascii import unhexlify

from .hashdragons import HashdragonDescriber
from .event import Event
from .transactions import *


# Class that handles the Wander dialog.
class WanderDialog(QDialog, MessageBoxMixin, PrintError):

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

        wandertolabel = QLabel("Wander to")

        self.layout.addWidget(wandertolabel, 0, 0)

        self.wander_to = QLineEdit()
        #self.wander_to = PayToEdit(self.main_window)
        wandertolabel.setBuddy(self.wander_to)
        self.layout.addWidget(self.wander_to, 0, 1)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
        self.result = None

    @staticmethod
    def parse_address(address):
        # if networks.net.SLPADDR_PREFIX not in address:
        #     address = networks.net.SLPADDR_PREFIX + ":" + address
        return Address.from_string(address)



    def create_wander(self):
        coins = self.main_window.wallet.get_spendable_coins(None, self.main_window.config)
        fee = None

        # Current location of the hashdragon, i.e. last valid tx for this hashdragon
        current_txn_ref = self.main_window.hashdragons[self.hashdragon.hashdragon()]
        ok, r = self.main_window.wallet.network.get_raw_tx_for_txid(current_txn_ref, timeout=10.0)

        output_index = -1

        if not ok:
            # FIXME Handle error properly.
            print("BlahBlah")
            return False
        else:
            tx = Transaction(r, sign_schnorr=self.main_window.wallet.is_schnorr_enabled())
            for vout in tx.get_outputs():
                d,index = vout
                if isinstance(d, ScriptOutput) and d.is_opreturn():
                    script = d.to_script()
                    ops = Script.get_ops(script)
                    i,lokad = ops[1]

                    if lokad == unhexlify('d101d400'):
                        _, o = ops[4]
                        output_index = int.from_bytes(o, 'big')
                        # If output_index far too big, we are probably dealing with Little Endian
                        if output_index >= 16777216:
                            output_index = int.from_bytes(o, 'little')


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
            flag = True
            for vout in tx.get_outputs():
                d,index = vout

                if isinstance(d, ScriptOutput) and d.is_opreturn():
                    script = d.to_script()
                    ops = Script.get_ops(script)
                    i,lokad = ops[1]

                    if lokad == unhexlify('d101d400'):
                        flag = False
            if flag and coin['value'] > 400:
                spendable_coins.append(coin)

        if len(spendable_coins) <= 0:
            self.main_window.show_message("Not enough coins for transfer.")
            return False

        inputs.append(spendable_coins[0])

        dest_address = self.wander_to.text() if self.wander_to.text() != '' else  None
        if dest_address is None:
            self.main_window.show_message("Invalid destination address.")
            return False

        outputs = []
        event = Event()

        op_return_script = event.build_hashdragon_op_return('wander', 0, 1, dest_address)
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

        ## Uncomment this to show transaction in popup for debug.
        #self.main_window.show_transaction(tx, None)

        status, msg = self.main_window.network.broadcast_transaction(tx)
        print("Status: ", status)
        print("msg: ", msg)

        # TODO Display confirmation message
        # TODO Reload hashdragon list in the main window.

        self.close()
        return True
