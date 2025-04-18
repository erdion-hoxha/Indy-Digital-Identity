import asyncio
import json
import os
from indy import pool, wallet, did, ledger, anoncreds
from indy.error import IndyError

async def setup_issuer():
    pool_name = 'von-network'
    wallet_name = 'issuer_wallet'
    wallet_key = 'issuer_wallet_key'
    genesis_path = 'config/genesis.txn'  

    wallet_config = json.dumps({"id": wallet_name})
    wallet_credentials = json.dumps({"key": wallet_key})
    pool_config = json.dumps({"genesis_txn": genesis_path})

    # CREATE + OPEN POOL
    try:
        await pool.set_protocol_version(2)

        try:
            await pool.create_pool_ledger_config(pool_name, pool_config)
            print("[SUCCESS] Pool config created")
        except IndyError as e:
            if "PoolLedgerConfigAlreadyExistsError" in str(e):
                print("[INFO] Pool config already exists, skipping creation")
            else:
                print(f"[FAILED] Pool config creation error: {e.message}")
                return

        pool_handle = await pool.open_pool_ledger(pool_name, None)
        print("[FAILED] Pool ledger opened")
    except IndyError as e:
        print(f"[FAILED] Pool error: {e.message}")
        return

    # CREATE WALLET
    try:
        await wallet.create_wallet(wallet_config, wallet_credentials)
        print(f"[SUCCESS] Created wallet: {wallet_name}")
    except IndyError as e:
        if "WalletAlreadyExistsError" in str(e):
            print("[INFO] Wallet already exists, opening...")
        else:
            print(f"[FAILED] Wallet creation error: {e.message}")
            return

    #  OPEN WALLET
    try:
        issuer_wallet = await wallet.open_wallet(wallet_config, wallet_credentials)
        print(f"[SUCCESS] Opened wallet: {wallet_name}")
    except IndyError as e:
        print(f"[FAILED] Wallet open error: {e.message}")
        return

    try:
        # CREATE TRUSTEE DID
        issuer_did, _ = await did.create_and_store_my_did(
            issuer_wallet,
            json.dumps({'seed': '000000000000000000000000Trustee1'})
        )
        print(f"[SUCCESS] DID created: {issuer_did}")

        # CREATE + PUBLISH SCHEMA
        schema_name = "NationalID"
        schema_version = "1.0"
        schema_attrs = json.dumps(["name", "dob", "citizen_id"])

        schema_id, schema_json = await anoncreds.issuer_create_schema(
            issuer_did, schema_name, schema_version, schema_attrs
        )
        schema_request = await ledger.build_schema_request(issuer_did, schema_json)
        await ledger.sign_and_submit_request(pool_handle, issuer_wallet, issuer_did, schema_request)
        print(f"[✔] Schema published: {schema_name}")

        # CREATE + PUBLISH CRED DEF
        cred_def_tag = "default"
        cred_def_config = json.dumps({"support_revocation": False})
        cred_def_id, cred_def_json = await anoncreds.issuer_create_and_store_credential_def(
            issuer_wallet, issuer_did, schema_json, cred_def_tag, "CL", cred_def_config
        )

        cred_def_request = await ledger.build_cred_def_request(issuer_did, cred_def_json)
        await ledger.sign_and_submit_request(pool_handle, issuer_wallet, issuer_did, cred_def_request)
        print(f"[SUCCESS] Credential definition published")

    except IndyError as e:
        print(f"[FAILED] Operation error: {e.message}")

    # CLEANUP
    await wallet.close_wallet(issuer_wallet)
    await pool.close_pool_ledger(pool_handle)
    print("[SUCCESS] Cleaned up resources")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(setup_issuer())
