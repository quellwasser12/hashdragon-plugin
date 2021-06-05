from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from electroncash import Transaction
from electroncash.util import PrintError
from electroncash.address import Address, ScriptOutput, Script
from electroncash.bitcoin import TYPE_ADDRESS, TYPE_SCRIPT

from binascii import unhexlify,hexlify

from .hashdragons import HashdragonDescriber
from .event import Event


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

    def parse_address(self, address):
        # if networks.net.SLPADDR_PREFIX not in address:
        #     address = networks.net.SLPADDR_PREFIX + ":" + address
        return Address.from_string(address)



    def create_wander(self):
        coins = self.main_window.wallet.get_spendable_coins(None, self.main_window.config)
        fee = None

        # Current location of the hashdragon, i.e. last valid tx for this hashdragon
        current_txn_ref = self.main_window.hashdragons[self.hashdragon.hashdragon()]
        print("Current txn ref: ", current_txn_ref)
        ok, r = self.main_window.wallet.network.get_raw_tx_for_txid(current_txn_ref, timeout=10.0)

        output_index = -1

        if not ok:
            print("BlahBlah")
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
                        if (output_index) >= 16777216:
                            output_index = int.from_bytes(o, 'little')
                        print("OUtput index = ", output_index)


        inputs = []

        # First entry is the vout of the previous valid tx
        for coin in coins:
            if coin['prevout_hash'] == current_txn_ref and coin['prevout_n'] == output_index:
                inputs.append(coin)

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
            return

#        inputs.append(spendable_coins[0])

        dest_address = self.wander_to.text() if self.wander_to.text() != '' else  None
        if dest_address is None:
            self.main_window.show_message("Invalid destination address.")
            return

        outputs = []
        event = Event()

        op_return_script = event.build_hashdragon_op_return('wander', 0, 1, dest_address)
        outputs.append((TYPE_SCRIPT, op_return_script, 0))

        addr = self.parse_address(dest_address)
        outputs.append((TYPE_ADDRESS, addr, 0))


        change_addresses = list(self.main_window.wallet.get_change_addresses())
        fee = 0

        print("Fee: ", inputs[0]['value'])
        # Use value of hashdragon input as fee.
        # Fee will be added later when solving disappearing input coin issue
        unsigned_tx = self.main_window.wallet.make_unsigned_transaction(inputs, outputs, self.main_window.config, inputs[0]['value'])

        # This is a massive kludge
        # coinchooser keeps removing input coin used to pay for the fee.
        # Therefore we create a separate transaction with the specific coin as an input,
        # so its fields can be set correctly, and add it back to the other tx once done.
        # We also copy the output to make sure we don't lose money in the process, and include the correct change.
        dummy_tx_to_create_input = self.main_window.wallet.make_unsigned_transaction([spendable_coins[0]], outputs, self.main_window.config, fee, change_addresses[-1])

        unsigned_tx.add_inputs(dummy_tx_to_create_input.inputs())
        unsigned_tx.add_outputs([dummy_tx_to_create_input.outputs()[-1]])

        print(unsigned_tx)
        print(unsigned_tx.inputs())


        self.result = QDialog.Accepted
       # try:
       #     tx = self.main_window.wallet.make_unsigned_transaction(coins, outputs, self.main_window.config, fee, None, mandatory_coins=[baton_input])
