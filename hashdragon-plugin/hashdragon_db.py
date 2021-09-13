"""
hashdragon-plugin.hashdragon_db

Db of the hashdragons living in the wallet.
"""


class HashdragonEntry:

    def __init__(self, h, state, current_tx, current_owner, index, hatched_block, hatched_tx):
        self.h = h
        self.state = state
        self.current_tx = current_tx
        self.current_owner = current_owner
        self.index = index
        self.hatched_block = hatched_block
        self.hatched_tx = hatched_tx
        self.lifeline = []

    def get_state(self) -> str:
        return self.state

    def get_current_tx(self) -> str:
        return self.current_tx

    def get_current_index(self) -> int:
        return self.index

    def get_hatched_block(self) -> int:
        return self.hatched_block

    def __repr__(self):
        return """{"h": "%s",
"state": "%s",
"current_tx": "%s",
"current_owner": "%s",
"index": %d,
"hatched_block": %d,
"hatched_tx": "%s"}""" % (self.h, self.state, self.current_tx, self.current_owner,
                          self.index, self.hatched_block, self.hatched_tx)


class HashdragonDb:

    def __init__(self):
        # The db is dictionary of HashdragonEntry entries
        # indexed by hash of the hashdragon
        self.db = dict()
        self.initialised = False

    def add_hashdragon(self, h, state, current_tx, current_owner, index, block, tx) -> HashdragonEntry:
        entry = HashdragonEntry(h, state, current_tx, current_owner, index, block, tx)
        new_db = self.db.copy()
        new_db[h] = entry
        self.db = new_db
        return entry

    def get_hashdragon_by_hash(self, h) -> HashdragonEntry:
        return self.db[h]

    def get_hashdragons_by_tx(self, txid) -> list[HashdragonEntry]:
        hashdragons = self.list_hashdragons()
        return list(filter(lambda h: h.get_current_tx() == txid, hashdragons))

    def list_hashdragons(self) -> list[HashdragonEntry]:
        keys = list(self.db.keys())
        keys.sort()
        return keys

    def is_ready(self) -> bool:
        return self.initialised

    def ready(self) -> None:
        self.initialised = True

    def dump(self) -> None:
        print(self.db)
