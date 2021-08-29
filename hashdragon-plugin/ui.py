from PyQt5.QtWidgets import *

from electroncash.i18n import _
from electroncash_gui.qt.util import MyTreeWidget, MessageBoxMixin

from .detail_dialog import DetailDialog
from .wander_dialog import WanderDialog
from .hibernate_dialog import HibernateDialog
from .breed_dialog import BreedDialog
from .hashdragons import Hashdragon


class Ui(MyTreeWidget, MessageBoxMixin):
    def __init__(self, plugin, parent, wallet_name):
        MyTreeWidget.__init__(self, parent, self.create_menu, [
            _('Hashdragon'),
            _('State'),
            _('Description'),
            _('Strength'),
            _('Colour'),
        ], 0, [])

        self.plugin = plugin
        self.wallet_name = wallet_name
        self.db = plugin.db

    def show_hashdragon_details(self, hashdragon):
        d = DetailDialog(hashdragon, self.parent)
        d.show()

    def show_hashdragon_wander(self, hashdragon):
        d = WanderDialog(hashdragon, self.parent)
        d.show()

    def show_hashdragon_hibernate(self, hashdragon):
        d = HibernateDialog(hashdragon, self.parent)
        d.show()

    def show_hashdragon_breed(self, chosen_hashdragon, hashdragons):
        d = BreedDialog(chosen_hashdragon, self.parent, hashdragons)
        d.show()

    def create_menu(self, position):
        hashdragon = self.currentItem()
        if not hashdragon:
            return

        hd_object = Hashdragon.from_hex_string(hashdragon.data(0, 0))

        menu = QMenu()
        menu.addAction(_('Details'), lambda: self.show_hashdragon_details(hd_object))
        menu.addSeparator()
        menu.addAction(_('Wander'), lambda: self.show_hashdragon_wander(hd_object))
        menu.addAction(_('Hibernate'), lambda: self.show_hashdragon_hibernate(hd_object))
        menu.addAction(_('Breed'), lambda: self.show_hashdragon_breed(hd_object, self.db))

        menu.exec_(self.viewport().mapToGlobal(position))

    def on_delete(self):
        pass

    def on_update(self):
        pass
