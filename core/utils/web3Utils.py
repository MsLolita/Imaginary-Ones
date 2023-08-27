from eth_account import Account


class Web3Utils:
    def __init__(self,  mnemonic: str = None, key: str = None):
        Account.enable_unaudited_hdwallet_features()
        if mnemonic:
            self.mnemonic = mnemonic
            self.acct = Account.from_mnemonic(mnemonic)
        elif key:
            self.mnemonic = ""
            self.acct = Account.from_key(key)

    def create_wallet(self):
        self.acct, self.mnemonic = Account.create_with_mnemonic()
        return self.acct, self.mnemonic
