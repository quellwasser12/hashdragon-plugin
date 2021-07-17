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
        self.hashdragon_state = dict()

    def fullname(self):
        return 'Hashdragon Plugin'

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

                # TODO Extract logic, and check command: hashdragon may not be in this script
                if lokad == unhexlify('d101d400'):

                    _, command = ops[2]
                    command_as_int = int.from_bytes(command, 'big')

                    # 209, d1, hatch
                    if command_as_int == 209:
                        # Command is hatch
                        i, hd = ops[6]

                        if depth == 0:
                            self.main_window.hashdragons[hd.hex()] = tx.txid()
                            self.current_state = 'Hatched'
                        else:
                            # If we are higher up in the history, retrieve original txn id
                            self.main_window.hashdragons[hd.hex()] = self.current_tx
                        return [hd.hex(), self.current_state]

                    # 210, d2, 5 args, wander
                    elif command_as_int == 210 and len(ops) <= 5:
                        # Command is wander
                        _, dest_index = ops[4]
                        dest_index = int.from_bytes(dest_index, 'big')
                        owner_vout, _ = tx.get_outputs()[dest_index]

                        # Only look into this hashdragon if we are the owner.
                        if wallet.is_mine(owner_vout):
                            _, input_index = ops[3]
                            input_index = int.from_bytes(input_index, 'big')
                            owner_vin = tx.inputs()[input_index]
                            ok, r = wallet.network.get_raw_tx_for_txid(owner_vin['prevout_hash'], timeout=10.0)

                            if depth == 0:
                                self.current_tx = tx.txid()
                                self.current_state = 'Wandering'

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
                        dest_index = int.from_bytes(dest_index, 'big')
                        owner_vout, _ = tx.get_outputs()[dest_index]

                        # Only look into this hashdragon if we are the owner.
                        if wallet.is_mine(owner_vout):

                            if depth == 0:
                                self.current_tx = tx.txid()
                                self.current_state = 'Rescued'

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
                        dest_index = int.from_bytes(dest_index, 'big')
                        owner_vout, _ = tx.get_outputs()[dest_index]

                        # Only look into this hashdragon if we are the owner.
                        if wallet.is_mine(owner_vout):

                            if depth == 0:
                                self.current_tx = tx.txid()
                                self.current_state = 'Hibernating'

                            _, input_index = ops[3]
                            input_index = int.from_bytes(input_index, 'big')
                            owner_vin = tx.inputs()[input_index]
                            ok, r = wallet.network.get_raw_tx_for_txid(owner_vin.prevout_hash, timeout=10.0)

                            if not ok:
                                print("Could not retrieve transaction.") # TODO handle error
                                return None
                            else:
                                tx0 = Transaction(r, sign_schnorr=wallet.is_schnorr_enabled())
                                return self.process_txn(tx0, wallet, depth+1)

    def extract_hashdragons(self, wallet, coins):
        """
        Extracts all the hashdragons in the wallet by going through all the transactions
        in the wallet.
        """
        txn_list = []
        self.main_window.hashdragons = dict()

        for coin in coins:
            tx = wallet.transactions.get(coin['prevout_hash'])
            val = self.process_txn(tx, wallet)

            # Add val if not in list already (multiple coins can be issued from the same txn)
            if val is not None:
                hd, state = val
                if hd not in txn_list:
                    txn_list.append(hd)
                    self.hashdragon_state[hd] = state

        txn_list.sort()
        return txn_list

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

        spendable_coins = wallet.get_spendable_coins(None, self.config)
        hashdragons = self.extract_hashdragons(wallet, spendable_coins)
        describer = HashdragonDescriber()

        for hd in hashdragons:
            hd_item = QTreeWidgetItem(ui)
            h = Hashdragon.from_hex_string(hd)
            hd_item.setData(0, 0, h.hashdragon())
            hd_item.setData(1, 0, self.hashdragon_state[h.hashdragon()])
            hd_item.setData(2, 0, describer.describe(h))
            hd_item.setData(3, 0, h.strength())
            r, g, b = h.colour_as_rgb()
            hd_item.setBackground(4, QBrush(QColor(r, g, b)))
            ui.addChild(hd_item)

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
        l = Ui(window, self, wallet_name)
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
