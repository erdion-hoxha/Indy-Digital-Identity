import json
from indy import wallet, error
from config.config import Config

class WalletManager:
    def __init__(self):
        self.config = Config()

    async def create_wallet(self, wallet_name, wallet_key):
        wallet_config = json.dumps({
            "id": wallet_name,
            "storage_config": {"path": self.config.WALLET_STORAGE}
        })
        wallet_credentials = json.dumps({
            "key": wallet_key,
            "storage_credentials": None
        })
        try:
            await wallet.create_wallet(wallet_config, wallet_credentials)
        except error.WalletAlreadyExistsError:
            print("Wallet already exists, opening the wallet instead.")
        except Exception as e:
            print(f"Wallet error: {str(e)}")
            raise
        return await wallet.open_wallet(wallet_config, wallet_credentials)

    async def close_wallet(self, wallet_handle):
        await wallet.close_wallet(wallet_handle)
