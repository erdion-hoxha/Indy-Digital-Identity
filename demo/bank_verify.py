import asyncio
import json
from indy import pool, anoncreds
from utils.von_ledger import VonLedger

async def verify():
    pool_handle = None
    try:
        # 1. Setup pool
        await pool.set_protocol_version(2)
        pool_handle = await pool.open_pool_ledger("von-network", None)

        # 2. Load proof data
        with open('proof_request.json') as f:
            proof_request = json.load(f)
        with open('proof.json') as f:
            proof = json.load(f)

        # 3. Get identifiers
        schema_id = proof['identifiers'][0]['schema_id']
        cred_def_id = proof['identifiers'][0]['cred_def_id']

        # 4. Fetch from ledger
        schema = await VonLedger.fetch_schema(pool_handle, schema_id)
        cred_def = await VonLedger.fetch_cred_def(pool_handle, cred_def_id)

        # 5. Verify proof
        valid = await anoncreds.verifier_verify_proof(
            json.dumps(proof_request),
            json.dumps(proof),
            json.dumps({schema_id: schema}),
            json.dumps({cred_def_id: cred_def}),
            json.dumps({}),
            json.dumps({})
        )

        print(f"\n🔍 Verification Result: {'VALID' if valid else 'INVALID'}")
        if valid:
            print("\nRevealed Attributes:")
            for attr in proof['requested_proof']['revealed_attrs'].values():
                print(f"  {attr['name']}: {attr['raw']}")

    except Exception as e:
        print(f" Verification failed: {str(e)}")
    finally:
        if pool_handle: await pool.close_pool_ledger(pool_handle)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(verify())