from electroncash.transaction import Transaction
from electroncash.coinchooser import CoinChooserPrivacy, PRNG

class SlpCoinChooser(CoinChooserPrivacy):
    def make_tx(self, coins, outputs, change_addrs, fee_estimator,
                dust_threshold, sign_schnorr=False, *, mandatory_coins=[]):
        '''Select unspent coins to spend to pay outputs.  If the change is
        greater than dust_threshold (after adding the change output to
        the transaction) it is kept, otherwise none is sent and it is
        added to the transaction fee.'''

        # Remove mandatory_coin items from coin chooser's list
        for c in mandatory_coins:
            for coin in coins.copy():
                if coin['prevout_hash'] == c['prevout_hash'] and coin['prevout_n'] == c['prevout_n']:
                    coins.remove(coin)

        # Deterministic randomness from coins
        utxos = [c['prevout_hash'] + str(c['prevout_n']) for c in coins]
        self.p = PRNG(''.join(sorted(utxos)))

        # Copy the ouputs so when adding change we don't modify "outputs"
        tx = Transaction.from_io([], outputs, sign_schnorr=sign_schnorr)
        # Size of the transaction with no inputs and no change
        base_size = tx.estimated_size()
        spent_amount = tx.output_value()

        def sufficient_funds(buckets):
            '''Given a list of buckets, return True if it has enough
            value to pay for the transaction'''
            mandatory_coins_bucket = self.bucketize_coins(mandatory_coins, sign_schnorr=sign_schnorr)
            mandatory_input = sum(coin.value for coin in mandatory_coins_bucket)
            mandatory_input_size = sum(coin.size for coin in mandatory_coins_bucket)
            total_input = sum(bucket.value for bucket in buckets) + mandatory_input
            total_size = sum(bucket.size for bucket in buckets) + mandatory_input_size + base_size
            return total_input >= spent_amount + fee_estimator(total_size)

        # Collect the coins into buckets, choose a subset of the buckets
        buckets = self.bucketize_coins(coins, sign_schnorr=sign_schnorr)
        buckets = self.choose_buckets(buckets, sufficient_funds, self.penalty_func(tx))

        tx.add_inputs(mandatory_coins)
        tx.add_inputs([coin for b in buckets for coin in b.coins])
        slp_size = sum(bucket.size for bucket in self.bucketize_coins(mandatory_coins))
        tx_size = base_size + sum(bucket.size for bucket in buckets) + slp_size

        # This takes a count of change outputs and returns a tx fee;
        # each pay-to-bitcoin-address output serializes as 34 bytes
        fee = lambda count: fee_estimator(tx_size + count * 34)
        change, dust = self.change_outputs(tx, change_addrs, fee, dust_threshold)
        tx.add_outputs(change)
        tx.ephemeral['dust_to_fee'] = dust

        self.print_error("using %d inputs" % len(tx.inputs()))
        self.print_error("using buckets:", [bucket.desc for bucket in buckets])

        return tx
