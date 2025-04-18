import asyncio
import json
import sys
from indy import pool, error

async def test_pool():
    try:
        print("\n=== Pool Connection Test ===")
        
        # 1. Set protocol version (critical first step)
        print("1. Setting protocol version (2)...")
        try:
            await pool.set_protocol_version(2)
            print("   ✓ Protocol version set")
        except Exception as e:
            print(f"   ✗ Failed to set protocol version: {str(e)}")
            return False

        # 2. Verify genesis file
        genesis_path = "config/genesis.txn"
        print(f"2. Using genesis file: {genesis_path}")
        try:
            with open(genesis_path) as f:
                genesis_data = f.read(100)  # Read first 100 chars
                print(f"   ✓ Genesis file exists (starts with): {genesis_data[:20]}...")
        except Exception as e:
            print(f"   ✗ Genesis file error: {str(e)}")
            return False

        # 3. Create pool config
        pool_config = json.dumps({
            "genesis_txn": genesis_path,
            "timeout": 120,
            "extended_timeout": 120
        })
        print("3. Creating pool config...")
        try:
            await pool.create_pool_ledger_config("test_pool", pool_config)
            print("   ✓ Pool config created")
        except error.IndyError as e:
            print(f"   ✗ Pool config creation failed: {e.message} (error code: {e.error_code})")
            return False

        # 4. Open pool with extended timeout
        print("4. Opening pool (timeout: 120s)...")
        try:
            pool_handle = await pool.open_pool_ledger(
                "test_pool", 
                json.dumps({"timeout": 120, "extended_timeout": 120})
            )
            print(f"   ✓ Pool opened successfully! Handle: {pool_handle}")
            
            # 5. Verify connection
            print("5. Verifying connection...")
            await pool.refresh_pool_ledger(pool_handle)
            print("   ✓ Pool refreshed successfully")
            
            # 6. Clean up
            print("6. Closing pool...")
            await pool.close_pool_ledger(pool_handle)
            await pool.delete_pool_ledger_config("test_pool")
            print("   ✓ Cleanup complete")
            
            print("\n=== TEST SUCCESSFUL ===")
            return True
            
        except error.IndyError as e:
            print(f"   ✗ Pool opening failed: {e.message} (error code: {e.error_code})")
            return False
            
    except Exception as e:
        print(f"\n!!! UNEXPECTED ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    result = asyncio.get_event_loop().run_until_complete(test_pool())
    sys.exit(0 if result else 1)