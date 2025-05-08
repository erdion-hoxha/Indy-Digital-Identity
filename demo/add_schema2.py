import asyncio
import json
from indy import pool, wallet, did, ledger, anoncreds
from indy.error import IndyError


async def setup_new_schema():
    pool_name = 'von-network'
    wallet_name = 'issuer_wallet'
    wallet_key = 'issuer_wallet_key'
    genesis_path = 'config/genesis.txn'

    wallet_config = json.dumps({"id": wallet_name})
    wallet_credentials = json.dumps({"key": wallet_key})
    pool_config = json.dumps({"genesis_txn": genesis_path})

    pool_handle = None
    issuer_wallet = None

    try:
        await pool.set_protocol_version(2)

        try:
            await pool.create_pool_ledger_config(pool_name, pool_config)
            print("[SUCCESS] Pool config created")
        except IndyError as e:
            if "already exists" in str(e):
                print("[INFO] Pool ledger config already exists")
            else:
                print(f"[FAILED] Pool config error: {e.message}")
                # return

        try:
            pool_handle = await pool.open_pool_ledger(pool_name, None)
            print("[SUCCESS] Pool ledger opened")
        except IndyError as e:
            print(f"[FAILED] Pool open error: {e.message}")
            return

        try:
            await wallet.create_wallet(wallet_config, wallet_credentials)
            print(f"[SUCCESS] Created wallet: {wallet_name}")
        except IndyError as e:
            if "already exists" in str(e):
                print("ℹINFO] Wallet already exists, opening...")
            else:
                print(f"[FAILED] Wallet creation error: {e.message}")
                # return

        issuer_wallet = await wallet.open_wallet(wallet_config, wallet_credentials)
        print(f"[SUCCESS] Opened wallet: {wallet_name}")

        issuer_did, _ = await did.create_and_store_my_did(
            issuer_wallet,
            json.dumps({'seed': '000000000000000000000000Trustee1'})
        )
        print(f"[SUCCESS] DID created: {issuer_did}")

        #  Create schema properly using anoncreds
        schema_name = "CollegeDegree"
        schema_version = "1.0"
        schema_attributes = ["name", "surname", "student_id", "university_name", "field_of_study", "degree", "graduation_date", "gpa", "country_of_issuance"]
        schema_id, schema_json = await anoncreds.issuer_create_schema(
            issuer_did, schema_name, schema_version, json.dumps(schema_attributes)
        )

        #  Build and publish the schema request
        schema_request = await ledger.build_schema_request(issuer_did, schema_json)
        await ledger.sign_and_submit_request(pool_handle, issuer_wallet, issuer_did, schema_request)
        print(f"[SUCCESS] Schema published: {schema_name} with ID: {schema_id}")

    except IndyError as e:
        print(f"[FAILED] Error: {e.message}")

    finally:
        if issuer_wallet:
            await wallet.close_wallet(issuer_wallet)
        if pool_handle:
            await pool.close_pool_ledger(pool_handle)
        print("[SUCCESS] Resources cleaned up")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(setup_new_schema())
