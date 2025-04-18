from indy import anoncreds
from .utils import wallet

class CitizenHolder:
    def __init__(self):
        self.wallet_handle = None
        
    async def setup(self, wallet_name, wallet_key):
        self.wallet_handle = await wallet.WalletManager.create_wallet(wallet_name, wallet_key)
        
    async def store_credential(self, cred_offer, cred_def_json):
        cred_request, _ = await anoncreds.prover_create_credential_req(
            self.wallet_handle, self.did, cred_offer, cred_def_json, self.master_secret_id)
        return cred_request