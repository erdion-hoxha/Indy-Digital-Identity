import asyncio
import json
from src.issuer import GovernmentIssuer
from src.holder import CitizenHolder
from src.verifier import ServiceVerifier

async def main():
    # Initialize components
    issuer = GovernmentIssuer()
    holder = CitizenHolder()
    verifier = ServiceVerifier()
    
    # Setup
    await issuer.setup("government_wallet", "gov123")
    await holder.setup("citizen_wallet", "citizen123")
    await verifier.setup("verifier_wallet", "verifier123")
    
    # Issue credential flow
    schema_id, schema_json = await issuer.create_schema(
        "NationalID", "1.0", ["name", "dob", "citizen_id"])
    
    # ... rest of your application flow

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())