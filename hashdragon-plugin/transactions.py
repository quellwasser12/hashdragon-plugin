from electroncash.address import Script, Address, ScriptOutput
from electroncash.coinchooser import CoinChooserPrivacy
from electroncash.plugins import run_hook


# Copied from Abstract_Wallet in Electron Cash
# This is to get around the fact that CoinChooser removes input.
def make_unsigned_transaction(wallet, inputs, outputs,
                              config,
                              fixed_fee=None, change_addr=None, sign_schnorr=None):
    '''
    sign_schnorr flag controls whether to mark the tx as signing with
        schnorr or not. Specify either a bool, or set the flag to 'None' to use
        whatever the wallet is configured to use from the GUI
    '''
    sign_schnorr = wallet.is_schnorr_enabled() if sign_schnorr is None else bool(sign_schnorr)
    # check outputs
    i_max = None
    for i, o in enumerate(outputs):
        _type, data, value = o
        if value == '!':
            if i_max is not None:
                raise BaseException("More than one output set to spend max")
            i_max = i

    # Avoid index-out-of-range with inputs[0] below
    if not inputs:
        raise NotEnoughFunds()

    if fixed_fee is None and config.fee_per_kb() is None:
        raise BaseException('Dynamic fee estimates not available')

    for item in inputs:
        wallet.add_input_info(item)

    # Fee estimator
    if fixed_fee is None:
        fee_estimator = config.estimate_fee
    else:
        fee_estimator = lambda size: fixed_fee

    if i_max is None:
        # Let the coin chooser select the coins to spend

        change_addrs = []
        if change_addr:
            change_addrs = [change_addr]

        if not change_addrs:
            # find a change addr from the change reservation subsystem
            max_change = wallet.max_change_outputs if wallet.multiple_change else 1
            if wallet.use_change:
                change_addrs = wallet.get_default_change_addresses(max_change)
            else:
                change_addrs = []

            if not change_addrs:
                # For some reason we couldn't get any autogenerated change
                # address (non-deterministic wallet?). So, try to find an
                # input address that belongs to us.
                for inp in inputs:
                    backup_addr = inp['address']
                    if wallet.is_mine(backup_addr):
                        change_addrs = [backup_addr]
                        break
                else:
                    # ok, none of the inputs are "mine" (why?!) -- fall back
                    # to picking first max_change change_addresses that have
                    # no history
                    change_addrs = []
                    for addr in wallet.get_change_addresses()[-wallet.gap_limit_for_change:]:
                        if wallet.get_num_tx(addr) == 0:
                            change_addrs.append(addr)
                            if len(change_addrs) >= max_change:
                                break
                    if not change_addrs:
                        # No unused wallet addresses or no change addresses.
                        # Fall back to picking ANY wallet address
                        try:
                            # Pick a random address
                            change_addrs = [random.choice(wallet.get_addresses())]
                        except IndexError:
                            change_addrs = []  # Address-free wallet?!
                    # This should never happen
                    if not change_addrs:
                        raise RuntimeError("Can't find a change address!")

        assert all(isinstance(addr, Address) for addr in change_addrs)

        coin_chooser = CoinChooserPrivacy()
        tx = coin_chooser.make_tx(inputs, outputs, change_addrs,
                                  fee_estimator, wallet.dust_threshold(), sign_schnorr=sign_schnorr)
    else:
        sendable = sum(map(lambda x:x['value'], inputs))
        _type, data, value = outputs[i_max]
        outputs[i_max] = (_type, data, 0)
        tx = Transaction.from_io(inputs, outputs, sign_schnorr=sign_schnorr)
        fee = fee_estimator(tx.estimated_size())
        amount = max(0, sendable - tx.output_value() - fee)
        outputs[i_max] = (_type, data, amount)
        tx = Transaction.from_io(inputs, outputs, sign_schnorr=sign_schnorr)

    # If user tries to send too big of a fee (more than 50 sat/byte),
    # stop them from shooting themselves in the foot
    tx_in_bytes = tx.estimated_size()
    fee_in_satoshis = tx.get_fee()
    sats_per_byte = fee_in_satoshis/tx_in_bytes

    if (sats_per_byte > 50):
        raise ExcessiveFee()

    # Sort the inputs and outputs deterministically
    tx.BIP_LI01_sort()
    # Timelock tx to current height.
    locktime = wallet.get_local_height()
    if locktime == -1: # We have no local height data (no headers synced).
        locktime = 0
    tx.locktime = locktime
    run_hook('make_unsigned_transaction', wallet, tx)

    return tx
