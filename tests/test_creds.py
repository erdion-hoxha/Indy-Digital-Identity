import asyncio
import json
import os
from indy import pool, ledger, error
from config.config import Config

async def get_schema(schema_id, pool_handle):
    try:
        # Build the GET_SCHEMA request.
        get_schema_request = await ledger.build_get_schema_request(None, schema_id)
        # Submit the request to the ledger.
        get_schema_response = await ledger.submit_request(pool_handle, get_schema_request)
        # Parse the response.
        parsed_schema_id, schema_json = await ledger.parse_get_schema_response(get_schema_response)
        return parsed_schema_id, json.loads(schema_json)
    except error.IndyError as e:
        print(f"Error fetching schema: {e.message} (error code: {e.error_code})")
        raise

async def main():
    # Set the protocol version.
    await pool.set_protocol_version(2)
    
    # Use the genesis file from your configuration.
    genesis_path = os.path.abspath("config/genesis.txn")
    print(f"Using genesis file: {genesis_path}")
    
    # Build pool configuration.
    pool_config = json.dumps({
        "genesis_txn": genesis_path,
        "timeout": 120,
        "extended_timeout": 120
    })

    pool_name = Config.POOL_NAME
    try:
        await pool.create_pool_ledger_config(pool_name, pool_config)
    except error.IndyError:
        print("Pool ledger config already exists, proceeding to open the pool.")
    
    pool_handle = await pool.open_pool_ledger(pool_name, json.dumps({"timeout": 120}))
    
    # Replace the schema_id below with the one that was published.
    schema_id = "V4SGRU86Z58d6TV7PBUe6f:2:NationalID:1.0"  # Use your actual schema ID
    try:
        queried_schema_id, schema = await get_schema(schema_id, pool_handle)
        print("Successfully retrieved schema by ID")
    except error.IndyError as e:
        print(f"Failed to get schema by ID: {e.message}")
        
        # Fallback: Try getting schema by sequence number
        seq_no = 123  # Replace with actual seq_no from publication response
        get_schema_request = await ledger.build_get_schema_request(None, None, seq_no)
        get_schema_response = await ledger.submit_request(pool_handle, get_schema_request)
        print("Raw response by seq_no:", get_schema_response)
    
    await pool.close_pool_ledger(pool_handle)

async def get_schema(schema_id, pool_handle):
    try:
        get_schema_request = await ledger.build_get_schema_request(None, schema_id)
        get_schema_response = await ledger.submit_request(pool_handle, get_schema_request)
        print("Raw GET_SCHEMA response:", get_schema_response)  # Debug output.
        parsed_schema_id, schema_json = await ledger.parse_get_schema_response(get_schema_response)
        return parsed_schema_id, json.loads(schema_json)
    except error.IndyError as e:
        print(f"Error fetching schema: {e.message} (error code: {e.error_code})")
        raise
    
if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
