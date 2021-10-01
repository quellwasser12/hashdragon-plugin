"""
hashdragon-plugin.qt

Main entry point for the Hashdragon Electron Cash plugin.
"""

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import electroncash.version
from electroncash import Transaction
from electroncash.i18n import _
from electroncash.plugins import BasePlugin, hook
from electroncash.address import Script, Address, ScriptOutput
from binascii import unhexlify,hexlify
from .hashdragons import Hashdragon, HashdragonDescriber
from .hashdragon_db import HashdragonDb
from .utils import find_owner_of_hashdragon, index_to_int, xor_arrays


class Plugin(BasePlugin):
    electrumcash_qt_gui = None
    # There's no real user-friendly way to enforce this.  So for now, we just calculate it, and ignore it.
    is_version_compatible = True

    def __init__(self, parent, config, name):
        BasePlugin.__init__(self, parent, config, name)

        self.wallet_windows = {}
        self.wallet_payment_tabs = {}
        self.wallet_payment_lists = {}

        self.current_tx = None
        self.current_state = None
        self.current_index = -1
        self.current_block = -1

        self.db = HashdragonDb()

    def fullname(self):
        return _("Hashdragon Plugin")

    def description(self):
        return _("Hashdragon Plugin")

    def is_available(self):
        if self.is_version_compatible is None:
            version = float(electroncash.version.PACKAGE_VERSION)
            self.is_version_compatible = version >= MINIMUM_ELECTRON_CASH_VERSION
        return True

    def on_close(self):
        """
        BasePlugin callback called when the wallet is disabled among other things.
        """
        for window in list(self.wallet_windows.values()):
            self.close_wallet(window.wallet)

    @hook
    def update_contact(self, address, new_entry, old_entry):
        print("update_contact", address, new_entry, old_entry)

    @hook
    def delete_contacts(self, contact_entries):
        print("delete_contacts", contact_entries)

    @hook
    def init_qt(self, qt_gui):
        """
        Hook called when a plugin is loaded (or enabled).
        """
        self.electrumcash_qt_gui = qt_gui
        # We get this multiple times.  Only handle it once, if unhandled.
        if len(self.wallet_windows):
            return

        # These are per-wallet windows.
        for window in self.electrumcash_qt_gui.windows:
            self.load_wallet(window.wallet, window)

    def process_txn(self, tx, wallet, depth=0):
        dest_index = -1
        for vout in tx.get_outputs():
            d, index = vout

            if isinstance(d, ScriptOutput) and d.is_opreturn():
                script = d.to_script()
                ops = Script.get_ops(script)
                i, lokad = ops[1]

                if lokad == unhexlify('d101d400'):

                    _, command = ops[2]
                    command_as_int = int.from_bytes(command, 'big')

                    # 209, d1, hatch
                    if command_as_int == 209:
                        # Command is hatch
                        i, hd = ops[6]
                        _, dest_index = ops[4]
                        dest_index = index_to_int(dest_index)

                        if depth == 0:
                            self.current_state = 'Hatched'
                            current_owner = find_owner_of_hashdragon(tx)
                            height, _, _ = wallet.get_tx_height(tx.txid())
                            self.db.add_hashdragon(hd.hex(), 'Hatched', tx.txid(), current_owner, dest_index, height, tx.txid())
                        else:
                            # If we are higher up in the history, retrieve txn id we started from.
                            current_owner = find_owner_of_hashdragon(self.current_tx)
                            height, _, _ = wallet.get_tx_height(tx.txid())
                            self.db.add_hashdragon(hd.hex(), self.current_state, self.current_tx.txid(),
                                                   current_owner, self.current_index, height, tx.txid())

                        return [hd.hex(), self.current_state]

                    # 210, d2, 5 args, wander
                    elif command_as_int == 210 and len(ops) <= 5:
                        # Command is wander
                        _, dest_index = ops[4]
                        dest_index = index_to_int(dest_index)
                        owner_vout, _ = tx.get_outputs()[dest_index]

                        # Only look into this hashdragon if we are the owner.
                        if wallet.is_mine(owner_vout):
                            _, input_index = ops[3]
                            input_index = index_to_int(input_index)
                            owner_vin = tx.inputs()[input_index]
                            ok, r = wallet.network.get_raw_tx_for_txid(owner_vin['prevout_hash'], timeout=10.0)

                            if depth == 0:
                                self.current_tx = tx
                                self.current_state = 'Wandering'
                                self.current_index = dest_index

                            if not ok:
                                print("Could not retrieve transaction.") # TODO handle error
                                return None
                            else:
                                tx0 = Transaction(r, sign_schnorr=wallet.is_schnorr_enabled())
                                return self.process_txn(tx0, wallet, depth+1)

                    # 210, d2, 6 args, rescue command
                    elif command_as_int == 210 and len(ops) > 5:
                        # Command is a rescue.
                        _, dest_index = ops[4]
                        dest_index = index_to_int(dest_index)
                        owner_vout, _ = tx.get_outputs()[dest_index]

                        # Only look into this hashdragon if we are the owner.
                        if wallet.is_mine(owner_vout):

                            if depth == 0:
                                self.current_tx = tx
                                self.current_state = 'Rescued'
                                self.current_index = dest_index

                            _, input_index = ops[3]
                            _, txn_ref = ops[5]

                            ok, r = wallet.network.get_raw_tx_for_txid(hexlify(txn_ref).decode(), timeout=10.0)
                            if not ok:
                                print("Could not retrieve transaction.") # TODO handle error
                                return None
                            else:
                                # Recursively call process_txn to find hashdragon.
                                tx0 = Transaction(r, sign_schnorr=wallet.is_schnorr_enabled())
                                return self.process_txn(tx0, wallet, depth+1)

                    # 211, d3, hibernate
                    elif command_as_int == 211:
                        # Command is hibernate
                        _, dest_index = ops[4]
                        dest_index = index_to_int(dest_index)
                        owner_vout, _ = tx.get_outputs()[dest_index]

                        # Only look into this hashdragon if we are the owner.
                        if wallet.is_mine(owner_vout):

                            if depth == 0:
                                self.current_tx = tx
                                self.current_state = 'Hibernating'
                                self.current_index = dest_index

                            _, input_index = ops[3]
                            input_index = index_to_int(input_index)
                            owner_vin = tx.inputs()[input_index]
                            ok, r = wallet.network.get_raw_tx_for_txid(owner_vin['prevout_hash'], timeout=10.0)

                            if not ok:
                                print("Could not retrieve transaction.") # TODO handle error
                                return None
                            else:
                                tx0 = Transaction(r, sign_schnorr=wallet.is_schnorr_enabled())
                                return self.process_txn(tx0, wallet, depth+1)
                    # 212, d4, breed
                    elif command_as_int == 212:
                        # Command is breed
                        _, dest_index = ops[7]
                        dest_index = index_to_int(dest_index)
                        owner_vout, _ = tx.get_outputs()[dest_index]

                        # Only look into this hashdragon if we are the owner.
                        if wallet.is_mine(owner_vout):

                            if depth == 0:
                                self.current_tx = tx
                                self.current_state = 'Spawn'
                                self.current_index = dest_index

                            # TODO Extract function for this pattern: get original txn for input index
                            # First hashdragon
                            _, input_index_1 = ops[3]
                            input_index_1 = index_to_int(input_index_1)
                            owner_vin_1 = tx.inputs()[input_index_1]
                            ok, r = wallet.network.get_raw_tx_for_txid(owner_vin_1['prevout_hash'], timeout=10.0)
                            hex_hashdragon_1 = None
                            if not ok:
                                print("Could not retrieve transaction.") # TODO handle error
                            else:
                                tx0 = Transaction(r, sign_schnorr=wallet.is_schnorr_enabled())
                                hex_hashdragon_1, _ = self.process_txn(tx0, wallet)

                            # Second hashdragon
                            _, input_index_2 = ops[5]
                            input_index_2 = index_to_int(input_index_2)
                            owner_vin_2 = tx.inputs()[input_index_2]
                            ok, r = wallet.network.get_raw_tx_for_txid(owner_vin_2['prevout_hash'], timeout=10.0)
                            hex_hashdragon_2 = None
                            if not ok:
                                print("Could not retrieve transaction.") # TODO handle error
                            else:
                                tx0 = Transaction(r, sign_schnorr=wallet.is_schnorr_enabled())
                                hex_hashdragon_2, _ = self.process_txn(tx0, wallet)

                            # Compute hash of spawn.
                            if hex_hashdragon_1 is not None and hex_hashdragon_2 is not None:
                                tx_block_hash = unhexlify(wallet.get_tx_block_hash(tx))
                                spawn = xor_arrays(unhexlify(hex_hashdragon_1),
                                                   xor_arrays(hex_hashdragon_2, tx_block_hash))
                                spawn[0] = b'\xd4'
                                print("Hex of the spawn: %s" % spawn)
                                return [spawn, self.current_state]
                                # TODO Add hashdragon to DB.

    def extract_hashdragons(self, wallet, coins):
        """
        Extracts all the hashdragons in the wallet by going through all the transactions
        in the wallet.
        """
        for coin in coins:
            tx = wallet.transactions.get(coin['prevout_hash'])
            self.process_txn(tx, wallet)

        self.db.ready()
        return self.db.list_hashdragons()

    def display_hashdragons(self, ui, wallet):
        spendable_coins = wallet.get_spendable_coins(None, self.config)
        hashdragons = self.extract_hashdragons(wallet, spendable_coins)
        describer = HashdragonDescriber()
        current_block = wallet.get_local_height()

        for hd in hashdragons:
            hd_entry = self.db.get_hashdragon_by_hash(hd)
            hd_item = QTreeWidgetItem(ui)
            h = Hashdragon.from_hex_string(hd)
            state = self.db.get_hashdragon_by_hash(hd).get_state()
            hd_item.setData(0, 0, h.hashdragon())
            hd_item.setData(1, 0, current_block >= (hd_entry.get_hatched_block() + h.maturity()))
            hd_item.setData(2, 0, state)
            hd_item.setData(3, 0, describer.describe(h))
            hd_item.setData(4, 0, h.strength())
            r, g, b = h.colour_as_rgb()
            hd_item.setBackground(5, QBrush(QColor(r, g, b)))
            ui.addChild(hd_item)

    @hook
    def load_wallet(self, wallet, window):
        """
        Hook called when a wallet is loaded and a window opened for it.
        """
        wallet_name = wallet.basename()
        self.main_window = window
        self.wallet_windows[wallet_name] = window
        self.add_ui_for_wallet(wallet_name, window)
        self.refresh_ui_for_wallet(wallet_name)

        ui = self.wallet_payment_lists[wallet_name]

        self.display_hashdragons(ui, wallet)

    @hook
    def update(self, wallet):
        wallet_name = wallet.basename()
        ui = self.wallet_payment_lists[wallet_name]
        ui.clear()

        self.display_hashdragons(ui, wallet)

    @hook
    def close_wallet(self, wallet):
        wallet_name = wallet.basename()
        window = self.wallet_windows[wallet_name]
        del self.wallet_windows[wallet_name]
        self.remove_ui_for_wallet(wallet_name, window)

    def _create_qicon(self):
        pixmap = QPixmap(40, 40)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setPen(Qt.black)
        painter.setFont(QFont("Times", 32, QFont.Bold))
        painter.drawText(QRect(0, 0, 40, 40), Qt.AlignCenter, u"\u136C")
        painter.end()
        return QIcon(pixmap)

    def add_ui_for_wallet(self, wallet_name, window):
        from .ui import Ui
        l = Ui(self, window, wallet_name)
        tab = window.create_list_tab(l)
        self.wallet_payment_tabs[wallet_name] = tab
        self.wallet_payment_lists[wallet_name] = l
        window.tabs.addTab(tab, self._create_qicon(), _('Hashdragons'))

    def remove_ui_for_wallet(self, wallet_name, window):

        wallet_tab = self.wallet_payment_tabs.get(wallet_name, None)
        if wallet_tab is not None:
            del self.wallet_payment_lists[wallet_name]
            del self.wallet_payment_tabs[wallet_name]
            i = window.tabs.indexOf(wallet_tab)
            window.tabs.removeTab(i)

    def refresh_ui_for_wallet(self, wallet_name):
        wallet_tab = self.wallet_payment_tabs[wallet_name]
        wallet_tab.update()
        wallet_tab = self.wallet_payment_lists[wallet_name]
        wallet_tab.update()
