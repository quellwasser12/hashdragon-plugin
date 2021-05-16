from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from electroncash.i18n import _
from electroncash_gui.qt.util import MyTreeWidget, MessageBoxMixin

from .detail_dialog import DetailDialog
from .hashdragons import Hashdragon


class Ui(MyTreeWidget, MessageBoxMixin):
    def __init__(self, parent, plugin, wallet_name):
        MyTreeWidget.__init__(self, parent, self.create_menu, [
            _('Hashdragon'),
            _('Description'),
            _('Strength'),
            _('Colour'),
        ], 0, [])

        self.plugin = plugin
        self.wallet_name = wallet_name

    def show_hashdragon_details(self, hashdragon):
        d = DetailDialog(hashdragon, self.parent)
        d.show()

    def create_menu(self, position):
        hashdragon = self.currentItem()
        if not hashdragon:
            return

        hd_object = Hashdragon.from_hex_string(hashdragon.data(0, 0))

        menu = QMenu()
        menu.addAction(_('Details'), lambda: self.show_hashdragon_details(hd_object))
        menu.addSeparator()
        menu.addAction(_('Wander'), lambda: print('Wander'))

        menu.exec_(self.viewport().mapToGlobal(position))

    def on_delete(self):
        pass

    def on_update(self):
        pass
