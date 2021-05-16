from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from electroncash.i18n import _
from electroncash_gui.qt.util import MyTreeWidget, MessageBoxMixin


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

    def create_menu(self, position):
        hashdragon = self.currentItem()
        if not hashdragon:
            return


        menu = QMenu()
        menu.addAction(_('Details'), lambda: print(hashdragon))
        menu.addSeparator()
        menu.addAction(_('Wander'), lambda: print('Wander'))

        menu.exec_(self.viewport().mapToGlobal(position))

    def on_delete(self):
        pass

    def on_update(self):
        pass
