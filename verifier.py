from indy import anoncreds
from .utils import pool, wallet

class ServiceVerifier:
    def __init__(self):
        self.wallet_handle = None
        
    async def setup(self, wallet_name, wallet_key):
        self.wallet_handle = await wallet.WalletManager.create_wallet(wallet_name, wallet_key)
        
    async def verify_proof(self, proof_request, proof):
        return await anoncreds.verifier_verify_proof(
            proof_request, proof, schemas_json, cred_defs_json, None, None)