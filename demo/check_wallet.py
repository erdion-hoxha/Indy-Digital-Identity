import asyncio
import json
from indy import wallet, did, anoncreds

async def inspect_citizen_wallet():
    # 1. Define the same config & creds you used when creating the wallet
    wallet_config = json.dumps({"id": "citizen_wallet"})
    wallet_credentials = json.dumps({"key": "citizen_wallet_key"})

    # 2. Open the wallet
    handle = await wallet.open_wallet(wallet_config, wallet_credentials)
    print("[✔] Opened citizen_wallet")

    # 3. List all DIDs you’ve stored in it
    dids_json = await did.list_my_dids_with_meta(handle)
    dids = json.loads(dids_json)
    print("\nDIDs in wallet:")
    for entry in dids:
        print("  •", entry)

    # 4. List all credentials in the wallet
    creds_json = await anoncreds.prover_get_credentials(handle, "{}")
    creds = json.loads(creds_json)
    print("\nCredentials in wallet:")
    for cred in creds:
        # each cred has referent, attrs, schema_id, cred_def_id, etc.
        print(f"  • referent={cred['referent']}, schema_id={cred['schema_id']}")
        print(f"    attributes: {cred['attrs']}\n")

    # 5. Close when done
    await wallet.close_wallet(handle)
    print("[✔] Closed citizen_wallet")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(inspect_citizen_wallet())
