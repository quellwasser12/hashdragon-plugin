from .base_event_dialog import BaseEventDialog


# Class that handles the Hibernate dialog.
class HibernateDialog(BaseEventDialog):

    def __init__(self, hashdragon, parent, db):
        BaseEventDialog.__init__(self, hashdragon, 'Hibernate', parent, db)

    def create_opreturn(self, args):
        event = args['event']
        dest_address = args['dest_address']
        return event.build_hashdragon_op_return('hibernate', 0, 1, dest_address)
