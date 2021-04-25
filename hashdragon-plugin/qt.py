from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import electroncash.version
from electroncash.i18n import _
from electroncash.plugins import BasePlugin, hook
from electroncash.address import Script, Address, ScriptOutput
from binascii import unhexlify
from .hashdragons import Hashdragon

class Plugin(BasePlugin):
    electrumcash_qt_gui = None
    # There's no real user-friendly way to enforce this.  So for now, we just calculate it, and ignore it.
    is_version_compatible = True

    def __init__(self, parent, config, name):
        BasePlugin.__init__(self, parent, config, name)

        self.wallet_windows = {}
        self.wallet_payment_tabs = {}
        self.wallet_payment_lists = {}

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


    def extract_hashdragons(self, wallet, coins):
        txn_list = []
        for coin in coins:
            tx = wallet.transactions.get(coin['prevout_hash'])

            for vout in tx.get_outputs():
                d,index = vout

                if isinstance(d, ScriptOutput) and d.is_opreturn():
                    script = d.to_script()
                    ops = Script.get_ops(script)
                    i,lokad = ops[1]

                    # TODO Extract logic, and check command: hashdragon may not be in this script
                    if lokad == unhexlify('d101d400'):
                        i,hd = ops[6]
                        txn_list.append(hd.hex())
        return txn_list

    @hook
    def load_wallet(self, wallet, window):
        """
        Hook called when a wallet is loaded and a window opened for it.
        """
        wallet_name = window.wallet.basename()
        self.wallet_windows[wallet_name] = window
        self.add_ui_for_wallet(wallet_name, window)
        self.refresh_ui_for_wallet(wallet_name)

        ui = self.wallet_payment_lists[wallet_name]

        spendable_coins = wallet.get_spendable_coins(None, self.config)
        hashdragons = self.extract_hashdragons(wallet, spendable_coins)

        for hd in hashdragons:
            hd_item = QTreeWidgetItem(ui)
            h = Hashdragon.from_hex_string(hd)
            hd_item.setData(0, 0, h.hashdragon())
            hd_item.setData(1, 0, h.strength())
            r, g, b = h.colour_as_rgb()
            hd_item.setBackground(2, QBrush(QColor(r, g, b)))
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
