from .base_event_dialog import BaseEventDialog


# Class that handles the Wander dialog.
class WanderDialog(BaseEventDialog):

    def __init__(self, hashdragon, parent, db):
        BaseEventDialog.__init__(self, hashdragon, 'Wander', parent, db)

    def create_opreturn(self, args):
        event = args['event']
        dest_address = args['dest_address']
        return event.build_hashdragon_op_return('wander', 0, 1, dest_address)
