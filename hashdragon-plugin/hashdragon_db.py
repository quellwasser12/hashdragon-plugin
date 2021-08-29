"""
hashdragon-plugin.hashdragon_db

Db of the hashdragons living in the wallet.
"""

import json
import inspect

class HashdragonEntry:

    def __init__(self, h, state, current_tx, current_owner):
        self.h = h
        self.state = state
        self.current_tx = current_tx
        self.current_owner = current_owner
        self.lifeline = []

    def get_state(self):
        return self.state

    def get_current_tx(self):
        return self.current_tx


class HashdragonEntryEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "__dict__"):
            return self.__dict__
        return obj


class HashdragonDb:

    def __init__(self):
        # The db is dictionary of HashdragonEntry entries
        # indexed by hash of the hashdragon
        self.db = dict()
        self.initialised = False

    def add_hashdragon(self, h, state, current_tx, current_owner):
        entry = HashdragonEntry(h, state, current_tx, current_owner)
        new_db = self.db.copy()
        new_db[h] = entry
        self.db = new_db
        return entry

    def get_hashdragon_by_hash(self, h):
        return self.db[h]

    def list_hashdragons(self):
        keys = list(self.db.keys())
        keys.sort()
        return keys

    def is_ready(self):
        return self.initialised

    def ready(self):
        self.initialised = True

    def dump(self):
       # print(json.dumps(self.db, cls=HashdragonEntryEncoder, indent=2, sort_keys=True, check_circular=False))
        print(self.db)
