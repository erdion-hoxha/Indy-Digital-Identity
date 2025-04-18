import json
from indy import pool, error
from config.config import Config
from indy import ledger

class LedgerUtils:
    def __init__(self):
        self.config = Config()
        self.pool_handle = None

    async def connect(self):
        pool_name = self.config.POOL_NAME
        try:
            # Build pool configuration with extended timeout parameters.
            pool_config = json.dumps({
                "genesis_txn": self.config.GENESIS_URL,
                "timeout": 120,           # Standard timeout in seconds.
                "extended_timeout": 180   # Extended timeout (if needed).
            })
            try:
                await pool.create_pool_ledger_config(pool_name, pool_config)
                print("Pool ledger config created.")
            except error.PoolLedgerConfigAlreadyExistsError:
                print("Pool ledger config already exists, proceeding to open the pool.")
            # Open the pool with extended timeout in the options.
            self.pool_handle = await pool.open_pool_ledger(
                pool_name, json.dumps({"timeout": 180, "extended_timeout": 180})
            )
            return self.pool_handle
        except Exception as e:
            print(f"Ledger connection error: {e}")
            raise

    async def disconnect(self):
        if self.pool_handle is not None:
            await pool.close_pool_ledger(self.pool_handle)
            
            
async def fetch_cred_def(pool_handle, cred_def_id):
    try:
        get_request = await ledger.build_get_cred_def_request(None, cred_def_id)
        response = await ledger.submit_request(pool_handle, get_request)
        return await ledger.parse_get_cred_def_response(response)
    except Exception as e:
        print(f"[!] Error fetching cred def: {str(e)}")
        # Try alternative parsing for VON network
        try:
            response_data = json.loads(response)
            if 'result' in response_data and 'data' in response_data['result']:
                return cred_def_id, response_data['result']['data']
        except:
            pass
        raise
    
async def get_schema(pool_handle, submitter_did, schema_id):
    try:
        request = await ledger.build_get_schema_request(submitter_did, schema_id)
        response = await ledger.submit_request(pool_handle, request)
        return await ledger.parse_get_schema_response(response)
    except error.IndyError as e:
        print(f"Error getting schema: {e.message}")
        raise

async def get_cred_def(pool_handle, submitter_did, cred_def_id):
    try:
        request = await ledger.build_get_cred_def_request(submitter_did, cred_def_id)
        response = await ledger.submit_request(pool_handle, request)
        return await ledger.parse_get_cred_def_response(response)
    except error.IndyError as e:
        print(f"Error getting credential definition: {e.message}")
        raise
    
    
async def fetch_von_cred_def(pool_handle, cred_def_id):
    """Special handler for VON Network's credential definition format"""
    try:
        request = await ledger.build_get_cred_def_request(None, cred_def_id)
        response = await ledger.submit_request(pool_handle, request)
        response_data = json.loads(response)
        
        if response_data.get('op') == 'REPLY' and 'result' in response_data:
            return cred_def_id, json.dumps(response_data['result']['data'])
        
        raise error.IndyError(extra={'message': 'Unexpected VON network response format'})
    except Exception as e:
        print(f"Raw VON response: {response}")
        raise error.IndyError(extra={'message': f"Failed to parse VON response: {str(e)}"})

async def fetch_von_schema(pool_handle, schema_id):
    """Standard schema fetch works fine with VON"""
    request = await ledger.build_get_schema_request(None, schema_id)
    response = await ledger.submit_request(pool_handle, request)
    return await ledger.parse_get_schema_response(response)



async def fetch_von_cred_def(pool_handle, cred_def_id):
    """Special handler for VON Network's credential definition format"""
    try:
        # Build and submit request
        request = await ledger.build_get_cred_def_request(None, cred_def_id)
        response = await ledger.submit_request(pool_handle, request)
        response_data = json.loads(response)
        
        # Handle VON Network's response format
        if response_data.get('op') == 'REPLY' and 'result' in response_data:
            cred_def_data = response_data['result']['data']
            if isinstance(cred_def_data, str):
                return cred_def_id, cred_def_data
            return cred_def_id, json.dumps(cred_def_data)
        
        raise error.IndyError(extra={'message': 'Unexpected VON network response format'})
    except Exception as e:
        print(f"[DEBUG] Raw VON response: {response}")
        raise error.IndyError(extra={'message': f"VON Network error: {str(e)}"})
