import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()  # Optionally load variables from .env

class Config:
    # Use the flat genesis file that we just created
    GENESIS_URL = os.getenv("INDY_GENESIS_URL", "config/genesis.txn")
    # Wallet storage directory (absolute path)
    WALLET_STORAGE = os.path.abspath(os.getenv("WALLET_STORAGE_PATH", "./wallet_storage"))
    # Name of the pool ledger config—make sure this is consistent across your scripts
    POOL_NAME = os.getenv("POOL_NAME", "von_network")

# Create the wallet storage directory if it doesn't exist.
Path(Config.WALLET_STORAGE).mkdir(parents=True, exist_ok=True)
