import asyncio
import json
import os
from indy import pool, wallet, did, ledger

# Configuration – adjust paths and names as necessary.
GENESIS_PATH = os.path.abspath("indy-identity-system/config/genesis.txn")
POOL_NAME = "von_network"
WALLET_CONFIG = json.dumps({"id": "demo_wallet"})
WALLET_CREDENTIALS = json.dumps({"key": "demo_wallet_key"})
SEED = "00000000000000000000000000000001" 

async def run_demo():
    print("Setting protocol version to 2...")
    await pool.set_protocol_version(2)

    # Verify that the genesis file exists.
    if not os.path.exists(GENESIS_PATH):
        print(f"Genesis file not found at: {GENESIS_PATH}")
        return
    else:
        print(f"Using genesis file at: {GENESIS_PATH}")

    # Create the pool configuration.
    pool_config = json.dumps({
        "genesis_txn": GENESIS_PATH
    })

    try:
        await pool.delete_pool_ledger_config(POOL_NAME)
        print("Deleted old pool ledger config.")
    except Exception as e:
        print("Note: Could not delete old pool ledger config, continuing...")

    try:
        print("Creating pool ledger config...")
        await pool.create_pool_ledger_config(POOL_NAME, pool_config)
        print("Pool ledger config created.")
    except Exception as e:
        print("Error creating pool ledger config:", e)
        return

    # Open the pool ledger connection.
    try:
        print("Opening pool ledger...")
        pool_handle = await pool.open_pool_ledger(POOL_NAME, None)
        print("Pool ledger opened successfully!")
    except Exception as e:
        print("Error opening pool ledger:", e)
        return

    # Create (or open) a wallet.
    try:
        print("Opening wallet...")
        wallet_handle = await wallet.open_wallet(WALLET_CONFIG, WALLET_CREDENTIALS)
        print("Wallet opened successfully!")
    except Exception:
        print("Wallet not found - Creating wallet...")
        try:
            wallet_handle = await wallet.create_wallet(WALLET_CONFIG, WALLET_CREDENTIALS)
            wallet_handle = await wallet.open_wallet(WALLET_CONFIG, WALLET_CREDENTIALS)
            print("  Wallet created and opened!")
        except Exception as e:
            print("  Error creating wallet:", e)
            await pool.close_pool_ledger(pool_handle)
            return

    # Create a new DID. Use the seed for deterministic DID creation (if desired).
    try:
        print("Creating a new DID...")
        (new_did, new_verkey) = await did.create_and_store_my_did(
            wallet_handle, json.dumps({"seed": SEED}))
        print(f"  Created DID: {new_did}")
        print(f"Verkey: {new_verkey}")
    except Exception as e:
        print(" Error creating DID:", e)
        await wallet.close_wallet(wallet_handle)
        await pool.close_pool_ledger(pool_handle)
        return

    # Build a sample schema (like NationalID).
    schema_data = {
        "name": "NationalID",
        "version": "1.0",
        "attr_names": ["name", "dob", "citizen_id"]
    }

    # Build a schema request.
    try:
        print("Building schema request...")
        schema_request = await ledger.build_schema_request(new_did, schema_data)
        print("Schema request created:")
        print(schema_request)
    except Exception as e:
        print("  Error building schema request:", e)
        await wallet.close_wallet(wallet_handle)
        await pool.close_pool_ledger(pool_handle)
        return

    # Sign and submit the schema request.
    try:
        print("Submitting schema request to ledger...")
        response = await ledger.sign_and_submit_request(
            pool_handle, wallet_handle, new_did, schema_request)
        response_data = json.loads(response)
        if response_data.get("op") == "REPLY":
            schema_id = f"{new_did}:2:{schema_data['name']}:{schema_data['version']}"
            print("  Schema published successfully!")
            print(f"Schema ID: {schema_id}")
            print("Transaction response:")
            print(json.dumps(response_data, indent=2))
        else:
            print("  Schema publication not successful:", response)
    except Exception as e:
        print("  Error submitting schema request:", e)

    # Clean up: close pool and wallet handles.
    await wallet.close_wallet(wallet_handle)
    await pool.close_pool_ledger(pool_handle)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(run_demo())
