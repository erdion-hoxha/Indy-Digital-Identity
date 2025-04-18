import asyncio
import json
from indy import wallet, anoncreds, pool
from utils.von_ledger import VonLedger

async def create_proof():
    wallet_handle = pool_handle = None
    
    try:
        # 1. Setup connections
        wallet_handle = await wallet.open_wallet(
            json.dumps({"id": "citizen_wallet"}),
            json.dumps({"key": "citizen_wallet_key"})
        )
        
        await pool.set_protocol_version(2)
        pool_handle = await pool.open_pool_ledger("von-network", None)

        # 2. Load proof request
        with open('proof_request.json') as f:
            proof_request = json.load(f)

        # 3. Get matching credentials
        search = await anoncreds.prover_search_credentials_for_proof_req(
            wallet_handle, json.dumps(proof_request), None)
        
        creds = json.loads(await anoncreds.prover_fetch_credentials_for_proof_req(
            search, 'attr1_referent', 10))[0]['cred_info']
        await anoncreds.prover_close_credentials_search_for_proof_req(search)

        print(f"🔍 Using Credential: {creds['referent']}")
        print(f"   Schema ID: {creds['schema_id']}")
        print(f"   Cred Def ID: {creds['cred_def_id']}")

        # 4. Fetch required ledger objects
        schema = await VonLedger.fetch_schema(pool_handle, creds['schema_id'])
        cred_def = await VonLedger.fetch_cred_def(pool_handle, creds['cred_def_id'])

        # 5. Create proof
        proof = await anoncreds.prover_create_proof(
            wallet_handle,
            json.dumps(proof_request),
            json.dumps({
                'self_attested_attributes': {},
                'requested_attributes': {
                    attr: {'cred_id': creds['referent'], 'revealed': True}
                    for attr in proof_request['requested_attributes']
                },
                'requested_predicates': {}
            }),
            "master_secret",
            json.dumps({creds['schema_id']: schema}),
            json.dumps({creds['cred_def_id']: cred_def}),
            json.dumps({})
        )

        with open('proof.json', 'w') as f:
            f.write(proof)
            
        print("✅ Proof created successfully!")
        print("Saved to proof.json")

    except Exception as e:
        print(f"❌ Failed to create proof: {str(e)}")
    finally:
        if wallet_handle: await wallet.close_wallet(wallet_handle)
        if pool_handle: await pool.close_pool_ledger(pool_handle)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(create_proof())