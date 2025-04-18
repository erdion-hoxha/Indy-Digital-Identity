import asyncio
import json
from indy import ledger, did, error
from indy_identity_system.wallet.wallet_manager import WalletManager
from indy_identity_system.ledger.ledger_utils import LedgerUtils

async def check_issuer_did(seed: str):
    print(f"Using seed: {seed}")
    wallet_mgr = WalletManager()
    # Create a temporary wallet for this test.
    wallet_handle = await wallet_mgr.create_wallet("check_wallet", "check_key")
    
    # Create a DID using the provided seed.
    did_config = {"seed": seed}
    my_did, verkey = await did.create_and_store_my_did(wallet_handle, json.dumps(did_config))
    print("Created DID:", my_did)
    print("Verification Key:", verkey)

    # Build a GET_NYM request for our DID.
    get_nym_request = await ledger.build_get_nym_request(None, my_did)
    print("\nGET_NYM request:", get_nym_request)

    # Connect to the ledger.
    ledger_utils = LedgerUtils()
    pool_handle = await ledger_utils.connect()

    # Submit the GET_NYM request.
    try:
        response = await ledger.submit_request(pool_handle, get_nym_request)
        print("\nRaw GET_NYM response:", response)
    except error.IndyError as e:
        print(f"\nError fetching NYM: {e.message} (error code: {e.error_code})")
    finally:
        # Clean up: Close wallet and disconnect ledger.
        await wallet_mgr.close_wallet(wallet_handle)
        await ledger_utils.disconnect()

if __name__ == "__main__":
    # Change the seed here to test. For a trusted DID on many networks, use:
    test_seed = "00000000000000000000000000000001"
    asyncio.get_event_loop().run_until_complete(check_issuer_did(test_seed))
