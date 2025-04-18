import asyncio
import json
from indy import ledger, error
from indy_identity_system.wallet.wallet_manager import WalletManager
from indy_identity_system.identities.issuer import GovernmentIssuer

async def test_schema_lifecycle():
    wallet_mgr = WalletManager()
    # Create the issuer wallet and get its handle.
    issuer_wallet_handle = await wallet_mgr.create_wallet("test_issuer_wallet", "issuer_key_123")
    issuer = GovernmentIssuer()
    try:
        # Set up issuer using the actual wallet handle.
        await issuer.setup(issuer_wallet_handle, seed="000000000000000000000000Trustee1")
        
        # Publish schema. (Note: our publish method returns 2 values.)
        schema_id, schema_json = await issuer.create_and_publish_schema(
            "NationalID", "1.0", ["name", "dob", "citizen_id"], issuer.ledger.pool_handle
        )
        
        # Query schema by ID.
        get_request = await ledger.build_get_schema_request(None, schema_id)
        response = await ledger.submit_request(issuer.ledger.pool_handle, get_request)
        print("Raw GET_SCHEMA response:", response)
        
        try:
            parsed_id, parsed_schema = await ledger.parse_get_schema_response(response)
            print(f"Schema verification successful!\nID: {parsed_id}\nSchema: {json.dumps(json.loads(parsed_schema), indent=2)}")
            result = True
        except error.IndyError as e:
            print(f"Schema verification failed. Raw response: {response}")
            result = False
    finally:
        await wallet_mgr.close_wallet(issuer_wallet_handle)
    return result

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(test_schema_lifecycle())
