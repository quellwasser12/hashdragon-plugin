"""
hashdragon-plugin.utils

Utilities to simplify hashdragon operations.

"""
from electroncash import Transaction
from electroncash.address import Script, Address, ScriptOutput
from binascii import unhexlify, hexlify


def index_to_int(index_bytes) -> int:
    """
    Converts the bytes of input_index/output_index of the hashdragon protocol into int.

    This takes into account the change from little endian to big endian at block
    """
    index = int.from_bytes(index_bytes, 'big')
    # If index far too big, we are probably dealing with Little Endian
    # FIXME Handle properly, should use block number (>= 683,000)
    if index >= 16777216:
        index = int.from_bytes(index_bytes, 'little')

    return index


def find_hashdragon_hash_from_script(wallet, tx) -> str:
    """
    Finds the hash of the hashdragon based on a given tx.
    """
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

                    return hd.hex()

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

                        if not ok:
                            print("Could not retrieve transaction.")  # TODO handle error
                            return None
                        else:
                            tx0 = Transaction(r, sign_schnorr=wallet.is_schnorr_enabled())
                            return find_hashdragon_hash_from_script(wallet, tx0)

                # 210, d2, 6 args, rescue command
                elif command_as_int == 210 and len(ops) > 5:
                    # Command is a rescue.
                    _, dest_index = ops[4]
                    dest_index = int.from_bytes(dest_index, 'big')
                    owner_vout, _ = tx.get_outputs()[dest_index]

                    # Only look into this hashdragon if we are the owner.
                    if wallet.is_mine(owner_vout):

                        _, txn_ref = ops[5]

                        ok, r = wallet.network.get_raw_tx_for_txid(hexlify(txn_ref).decode(), timeout=10.0)
                        if not ok:
                            print("Could not retrieve transaction.")  # TODO handle error
                            return None
                        else:
                            # Recursively call process_txn to find hashdragon.
                            tx0 = Transaction(r, sign_schnorr=wallet.is_schnorr_enabled())
                            return find_hashdragon_hash_from_script(wallet, tx0)

                # 211, d3, hibernate
                elif command_as_int == 211:
                    # Command is hibernate
                    _, dest_index = ops[4]
                    dest_index = int.from_bytes(dest_index, 'big')
                    owner_vout, _ = tx.get_outputs()[dest_index]

                    # Only look into this hashdragon if we are the owner.
                    if wallet.is_mine(owner_vout):

                        _, input_index = ops[3]
                        input_index = int.from_bytes(input_index, 'big')
                        owner_vin = tx.inputs()[input_index]
                        ok, r = wallet.network.get_raw_tx_for_txid(owner_vin['prevout_hash'], timeout=10.0)

                        if not ok:
                            print("Could not retrieve transaction.")  # TODO handle error
                            return None
                        else:
                            tx0 = Transaction(r, sign_schnorr=wallet.is_schnorr_enabled())
                            return find_hashdragon_hash_from_script(wallet, tx0)


def find_last_valid_tx_for_hashdragon(wallet, hashdragon, config):
    """
    Returns the last valid transaction for a hashdragon in a wallet.
    """
    spendable_coins = wallet.get_spendable_coins(None, config)
    for coin in spendable_coins:
        tx = wallet.transactions.get(coin['prevout_hash'])
        hashdragon_hex = find_hashdragon_hash_from_script(wallet, tx)
        if hashdragon_hex is not None and hashdragon_hex == hashdragon:
            return tx

    return None


def find_owner_of_hashdragon(tx) -> Address:
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
                if command_as_int in [209, 210, 211]:
                    i, dest_index = ops[4]
                    dest_index = index_to_int(dest_index)
                    owner_vout, _ = tx.get_outputs()[dest_index]

                    # Return the vout, of type Address
                    assert isinstance(owner_vout, Address), "Something wrong: owner should be Address."
                    return owner_vout
                elif command_as_int == 212:
                    i, dest_index = ops[7]
                    dest_index = index_to_int(dest_index)
                    owner_vout, _ = tx.get_outputs()[dest_index]

                    # Return the vout, of type Address
                    assert isinstance(owner_vout, Address), "Something wrong: owner should be Address."
                    return owner_vout
    return None


def xor_arrays(one, two) -> bytes:
    return bytes(a ^ b for a, b in zip(one, two))


def current_block_ref(wallet) -> str:
    local_height = wallet.get_local_height()
    return wallet.get_block_hash(local_height)


def count_leading_zeroes(h) -> int:
    count = 0
    for i in h:
        if i == '0':
            count += 1
        else:
            break
    return count
