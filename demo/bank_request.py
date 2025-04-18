import asyncio
import json
from indy import anoncreds

async def create_proof_request():
    nonce = await anoncreds.generate_nonce()
    
    proof_request = {
        'nonce': nonce,
        'name': 'Bank Verification',
        'version': '1.0',
        'requested_attributes': {
            'attr1_referent': {
                'name': 'name',
                'restrictions': [{
                    'schema_id': 'V4SGRU86Z58d6TV7PBUe6f:2:PersonIdentity:1.0',
                    'schema_name': 'PersonIdentity',
                    'schema_version': '1.0'
                }]
            }
        },
        'requested_predicates': {}
    }

    with open('proof_request.json', 'w') as f:
        json.dump(proof_request, f, indent=2)
    print("✅ Proof request created")

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(create_proof_request())