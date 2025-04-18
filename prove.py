import asyncio
import json
from indy import pool
from indy_identity_system.wallet.wallet_manager import WalletManager
from indy_identity_system.identities.issuer import GovernmentIssuer

async def main():
    # 1. First create and connect to the pool
    pool_name = "von_network"
    
    # Path to your genesis transaction file (adjust as needed)
    genesis_file_path = "config/genesis.txn"  # Update this path
    
    try:
        # Create pool configuration - must pass as JSON string
        pool_config = json.dumps({"genesis_txn": genesis_file_path})
        await pool.create_pool_ledger_config(pool_name, pool_config)
        
        # Open pool connection
        pool_handle = await pool.open_pool_ledger(pool_name, None)
        print(f"Successfully connected to pool with handle: {pool_handle}")
        
        # 2. Now proceed with wallet and issuer setup
        wallet_mgr = WalletManager()
        issuer_wallet_handle = await wallet_mgr.create_wallet("issuer_wallet", "issuer_key_123")
        
        issuer = GovernmentIssuer()
        await issuer.setup(issuer_wallet_handle, seed="000000000000000000000000Trustee1")
        
        # 3. Publish schema using the pool handle we created
        schema_id, schema_json = await issuer.create_and_publish_schema(
            "NationalID", "1.0", ["name", "dob", "citizen_id"], pool_handle
        )
        
        print(f"Published schema with ID: {schema_id}")
        
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        # Cleanup
        if 'issuer_wallet_handle' in locals():
            await wallet_mgr.close_wallet(issuer_wallet_handle)
        if 'issuer' in locals():
            await issuer.close()
        if 'pool_handle' in locals():
            await pool.close_pool_ledger(pool_handle)
        await pool.delete_pool_ledger_config(pool_name)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())