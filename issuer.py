import json
from indy import anoncreds, did, ledger, error
from indy_identity_system.ledger.ledger_utils import LedgerUtils

class GovernmentIssuer:
    def __init__(self):
        # Instantiate the ledger utility.
        self.ledger = LedgerUtils()
        self.wallet_handle = None
        self.issuer_did = None

    async def setup(self, wallet_handle, seed: str = None):
        """
        Sets up the issuer by saving the wallet handle,
        connecting to the ledger, and creating the issuer DID.
        """
        self.wallet_handle = wallet_handle
        # Connect to the ledger (this will set self.ledger.pool_handle).
        await self.ledger.connect()
        # Use the provided seed to generate a deterministic DID.
        did_config = {"seed": seed} if seed else {}
        self.issuer_did, _ = await did.create_and_store_my_did(wallet_handle, json.dumps(did_config))
        print(f"Issuer DID: {self.issuer_did}")

    async def create_and_publish_schema(self, schema_name: str, schema_version: str, attributes: list, pool_handle):
        """
        Creates a schema locally and publishes it to the ledger.
        Returns (schema_id, schema_json).
        """
        schema_id, schema_json = await anoncreds.issuer_create_schema(
            self.issuer_did, schema_name, schema_version, json.dumps(attributes)
        )
        print(f"Local schema created with ID: {schema_id}")
        schema_request = await ledger.build_schema_request(self.issuer_did, schema_json)
        print("Schema request created:", schema_request)
        try:
            response = await ledger.sign_and_submit_request(
                pool_handle,
                self.wallet_handle,
                self.issuer_did,
                schema_request
            )
            print("Publish response:", response)
            if response.get("op") == "REQNACK":
                raise Exception(f"Schema publish failed: {response.get('reason')}")
            print("Schema published on the ledger successfully.")
        except error.IndyError as e:
            print(f"Error publishing schema: {e.message} (error code: {e.error_code})")
            raise
        return schema_id, schema_json

    async def close(self):
        """
        Closes the issuer's ledger connection.
        """
        await self.ledger.disconnect()
