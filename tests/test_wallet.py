import pytest
from indy_identity_system.wallet.wallet_manager import WalletManager
from indy_identity_system.wallet.wallet_utils import WalletUtils
import asyncio
from indy_identity_system.identities.issuer import GovernmentIssuer

@pytest.mark.asyncio
async def test_wallet_creation():
    wallet_mgr = WalletManager()
    wallet_handle = await wallet_mgr.create_wallet("test_wallet", "test123")
    assert wallet_handle is not None
    await wallet_mgr.close_wallet(wallet_handle)
    
    
async def demo_create_did():
    wallet_mgr = WalletManager()
    wallet_handle = await wallet_mgr.create_wallet("test_wallet", "test_key_123")
    # Optionally, pass a seed for deterministic DID generation
    my_did, verkey = await WalletUtils.create_did(wallet_handle, seed="000000000000000000000000Trustee1")
    print(f"New DID: {my_did}\nVerification Key: {verkey}")
    await wallet_mgr.close_wallet(wallet_handle)

asyncio.get_event_loop().run_until_complete(demo_create_did())


async def demo_create_schema():
    wallet_mgr = WalletManager()
    # Open issuer wallet
    issuer_wallet = await wallet_mgr.create_wallet("issuer_wallet", "issuer_key_123")
    
    # Set up the issuer; passing a seed will generate a predictable DID if needed.
    issuer = GovernmentIssuer()
    await issuer.setup(issuer_wallet, seed="000000000000000000000000Trustee1")
    
    # Create a schema for a credential—e.g., National ID with four attributes.
    schema_name = "NationalID"
    schema_version = "1.0"
    attributes = ["name", "dob", "citizenship_number", "expiry_date"]
    schema_id, schema_json = await issuer.create_schema(schema_name, schema_version, attributes)
    print(f"Schema created with ID: {schema_id}")
    
    await wallet_mgr.close_wallet(issuer_wallet)

asyncio.get_event_loop().run_until_complete(demo_create_schema())
