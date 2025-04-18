import json
import asyncio
from indy import pool

class PoolManager:
    @staticmethod
    async def open_pool():
        await pool.set_protocol_version(2)
        pool_config = json.dumps({"genesis_txn": "config/genesis.txn"})
        try:
            await pool.create_pool_ledger_config("von_network", pool_config)
            return await pool.open_pool_ledger("von_network", None)
        except Exception as e:
            print(f"Pool error: {str(e)}")
            raise