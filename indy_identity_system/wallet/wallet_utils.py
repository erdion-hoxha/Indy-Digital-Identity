import json
from indy import did  # This is the module from Indy SDK

class WalletUtils:
    @staticmethod
    async def create_did(wallet_handle, seed: str = None):
        """
        Creates and stores a new DID in the wallet.
        
        :param wallet_handle: Open wallet handle.
        :param seed: Optional seed for deterministic DID generation.
        :return: A tuple (my_did, verkey).
        """
        did_config = {"seed": seed} if seed else {}
        # Rename the local variable from 'did' to 'my_did'
        (my_did, verkey) = await did.create_and_store_my_did(wallet_handle, json.dumps(did_config))
        return my_did, verkey
