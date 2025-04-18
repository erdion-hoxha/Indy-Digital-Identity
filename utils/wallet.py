import json
from indy import wallet

class WalletManager:
    @staticmethod
    async def create_wallet(wallet_name, wallet_key):
        config = json.dumps({"id": wallet_name})
        credentials = json.dumps({"key": wallet_key})
        try:
            await wallet.create_wallet(config, credentials)
            return await wallet.open_wallet(config, credentials)
        except Exception as e:
            print(f"Wallet error: {str(e)}")
            raise