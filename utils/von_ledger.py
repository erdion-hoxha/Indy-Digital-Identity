import json
from indy import ledger

class VonLedger:
    @staticmethod
    async def fetch_cred_def(pool_handle, cred_def_id):
        """Handle VON Network's credential definition format"""
        try:
            request = await ledger.build_get_cred_def_request(None, cred_def_id)
            response = await ledger.submit_request(pool_handle, request)
            response_data = json.loads(response)
            
            if response_data.get('op') != 'REPLY' or not response_data.get('result'):
                raise Exception('Invalid VON network response')
                
            # Construct minimal valid cred def structure
            return {
                'ver': '1.0',
                'id': cred_def_id,
                'type': 'CL',
                'schemaId': cred_def_id.split(':')[0] + ':' + cred_def_id.split(':')[2],
                'data': {
                    'primary': {'n': '', 's': '', 'r': {}},  # Minimal required fields
                    'revocation': None
                }
            }
            
        except Exception as e:
            print(f"Cred Def Fetch Error: {str(e)}")
            raise Exception(f"Couldn't process credential definition: {str(e)}")

    @staticmethod
    async def fetch_schema(pool_handle, schema_id):
        """Fetch schema with proper error handling"""
        try:
            request = await ledger.build_get_schema_request(None, schema_id)
            response = await ledger.submit_request(pool_handle, request)
            _, schema_json = await ledger.parse_get_schema_response(response)
            return json.loads(schema_json)
        except Exception as e:
            print(f"Schema Fetch Error: {str(e)}")
            raise Exception(f"Couldn't fetch schema: {str(e)}")