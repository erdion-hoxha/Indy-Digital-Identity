import asyncio
from indy_identity_system.wallet.wallet_manager import WalletManager
from indy_identity_system.identities.issuer import GovernmentIssuer

async def setup_ledger():
    print("Setting up initial ledger configuration...")
    
    # Create trustee wallet
    wallet_mgr = WalletManager()
    trustee_wallet = await wallet_mgr.create_wallet("trustee_wallet", "trustee123")
    
    # Initialize trustee
    trustee = GovernmentIssuer()
    await trustee.setup(trustee_wallet, "000000000000000000000000Trustee1")
    
    print("Ledger setup complete")
    await wallet_mgr.close_wallet(trustee_wallet)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(setup_ledger())
