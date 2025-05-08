import asyncio
import json
from indy import pool, wallet, did, anoncreds, ledger
from indy.error import IndyError
from pathlib import Path

async def main():
    pool_name = "von-network"
    genesis_path = "config/genesis.txn"
    wallet_config = json.dumps({"id": "issuer_wallet"})
    wallet_credentials = json.dumps({"key": "issuer_wallet_key"})
    holder_wallet_config = json.dumps({"id": "citizen_wallet"})
    holder_wallet_credentials = json.dumps({"key": "citizen_wallet_key"})

    schema_name = "CollegeDegree"
    schema_version = "1.0"

    try:
        # 1. SETUP POOL AND WALLETS ===========================================
        await pool.set_protocol_version(2)
        
        # Handle pool config
        try:
            await pool.create_pool_ledger_config(pool_name, json.dumps({"genesis_txn": str(Path(genesis_path).resolve())}))
            print("[SUCCESS] Created pool config")
        except IndyError as e:
            if "PoolLedgerConfigAlreadyExistsError" in str(e):
                print("[INFO] Using existing pool config")
            else:
                print(f"[FAILED] Pool config error: {e.message}")

        pool_handle = await pool.open_pool_ledger(pool_name, None)
        print("[SUCCESS] Pool opened")

        # Open issuer wallet
        try:
            issuer_wallet = await wallet.open_wallet(wallet_config, wallet_credentials)
            print("[SUCCESS] Issuer wallet opened")
        except IndyError as e:
            print(f"[FAILED] Issuer wallet error: {e.message}")
            return

        # 2. CREATE OR FETCH SCHEMA ===========================================
        issuer_did, _ = await did.create_and_store_my_did(
            issuer_wallet,
            json.dumps({'seed': '000000000000000000000000Trustee1'})
        )
        print(f"[SUCCESS] Issuer DID: {issuer_did}")

        schema_id = f"{issuer_did}:2:{schema_name}:{schema_version}"
        
        # Build and submit get_schema request
        get_schema_request = await ledger.build_get_schema_request(None, schema_id)
        get_schema_response = await ledger.submit_request(pool_handle, get_schema_request)
        
        try:
            # Get the schema JSON from the tuple
            (received_schema_id, schema_json) = await ledger.parse_get_schema_response(get_schema_response)
            print(f"[SUCCESS] Found existing schema: {received_schema_id}")
        except IndyError:
            # Schema doesn't exist, create new one
            schema_id, schema_json = await anoncreds.issuer_create_schema(
                issuer_did, schema_name, schema_version, 
                json.dumps(["name", "surname", "dob", "gender", "address", "national_id", "citizenship"])
            )
            
            # Publish schema to ledger
            schema_request = await ledger.build_schema_request(issuer_did, schema_json)
            await ledger.sign_and_submit_request(pool_handle, issuer_wallet, issuer_did, schema_request)
            print(f"[SUCCESS] Created and published new schema: {schema_id}")

        # 3. CREATE CREDENTIAL DEFINITION =====================================
        # Ensure schema_json is a string, not a tuple
        if isinstance(schema_json, tuple):
            schema_json = json.dumps(schema_json[1])  # Get the schema definition part

        cred_def_id, cred_def_json = await anoncreds.issuer_create_and_store_credential_def(
            issuer_wallet, issuer_did, schema_json, "TAG1", "CL", 
            json.dumps({"support_revocation": False})
        )
        print(f"[SUCCESS] Credential definition created: {cred_def_id}")

        # — Publish cred‑def to ledger — 
        cd_request = await ledger.build_cred_def_request(issuer_did, cred_def_json)
        await ledger.sign_and_submit_request(pool_handle, issuer_wallet, issuer_did, cd_request)
        print(f"[SUCCESS] Published credential definition to ledger: {cred_def_id}")

        # 4. ISSUE CREDENTIAL TO HOLDER =======================================
        # Create or open holder wallet
        try:
            await wallet.create_wallet(holder_wallet_config, holder_wallet_credentials)
            print("[SUCCESS] Created holder wallet")
        except IndyError:
            print("[INFO] Using existing holder wallet")
            
        holder_wallet = await wallet.open_wallet(holder_wallet_config, holder_wallet_credentials)
        holder_did, _ = await did.create_and_store_my_did(holder_wallet, "{}")
        print(f"[SUCCESS] Holder DID: {holder_did}")

        # Create master secret
        try:
            master_secret_id = await anoncreds.prover_create_master_secret(holder_wallet, None)
        except IndyError as e:
            if "AnoncredsMasterSecretDuplicateNameError" in str(e):
                master_secret_id = "master_secret"
            else:
                print(f"[FAILED] Master secret error: {e.message}")
                return

        # Create and issue credential
        cred_offer = await anoncreds.issuer_create_credential_offer(issuer_wallet, cred_def_id)
        (cred_req, cred_req_metadata) = await anoncreds.prover_create_credential_req(
            holder_wallet, holder_did, cred_offer, cred_def_json, master_secret_id
        )

        cred_values = json.dumps({
            "name": {"raw": "Bob", "encoded": ""},
            "surname": {"raw": "Dylan", "encoded": ""},
            "student_id": {"raw": "94105796", "encoded": ""},
            "university_name": {"raw": "UIUC", "encoded": ""},
            "field_of_study": {"raw": "Electrical Engineering", "encoded": ""},
            "degree": {"raw": "PhD", "encoded": ""},
            "graduation_date": {"raw": "2025-12-31", "encoded": ""}
            "gpa": {"raw": "4.0", "encoded": }
            "country_of_issuance": {"raw": "USA", "encoded": }
        })

        (credential, _, _) = await anoncreds.issuer_create_credential(
            issuer_wallet, cred_offer, cred_req, cred_values, None, None
        )

        await anoncreds.prover_store_credential(
            holder_wallet, None, cred_req_metadata, credential, cred_def_json, None
        )
        print("[SUCCESS] Credential issued and stored")

    except IndyError as e:
        print(f"[FAILED] Error: {e.message}")
    except Exception as e:
        print(f"[FAILED] Unexpected error: {str(e)}")
    finally:
        # Cleanup
        if 'issuer_wallet' in locals():
            await wallet.close_wallet(issuer_wallet)
        if 'holder_wallet' in locals():
            await wallet.close_wallet(holder_wallet)
        if 'pool_handle' in locals():
            await pool.close_pool_ledger(pool_handle)
        print("[SUCCESS] Resources cleaned up")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
