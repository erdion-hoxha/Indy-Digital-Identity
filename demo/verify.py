import asyncio
import json
from indy import pool, wallet, ledger, anoncreds
from indy.error import IndyError

PROTOCOL_VERSION = 2

async def build_gender_name_proof_request(schema_id: str) -> str:
    """
    Verifier: request Alice to reveal name, surname, and gender.
    """
    nonce = await anoncreds.generate_nonce()
    proof_req = {
        "nonce": nonce,
        "name": "gender_name_proof",
        "version": "1.0",
        "requested_attributes": {
            "attr_name_referent": {
                "name": "name",
                "restrictions": [{"schema_id": schema_id}]
            },
            "attr_surname_referent": {
                "name": "surname",
                "restrictions": [{"schema_id": schema_id}]
            },
            "attr_gender_referent": {
                "name": "gender",
                "restrictions": [{"schema_id": schema_id}]
            }
        },
        "requested_predicates": {}
    }
    print("→ proof_request:", json.dumps(proof_req, indent=2))
    return json.dumps(proof_req)


async def prover_create_gender_name_proof(
    wallet_handle,
    proof_req_json: str,
    master_secret_id: str,
    schema_id: str,
    cred_def_id: str,
    schema_json: str,
    cred_def_json: str
) -> str:
    """
    Prover: fetch the three requested attributes and build the proof.
    """
    search = await anoncreds.prover_search_credentials_for_proof_req(
        wallet_handle, proof_req_json, None
    )

    # fetch credentials for each referent
    creds_name     = await anoncreds.prover_fetch_credentials_for_proof_req(search, "attr_name_referent", 10)
    creds_surname  = await anoncreds.prover_fetch_credentials_for_proof_req(search, "attr_surname_referent", 10)
    creds_gender   = await anoncreds.prover_fetch_credentials_for_proof_req(search, "attr_gender_referent", 10)
    await anoncreds.prover_close_credentials_search_for_proof_req(search)

    ci_name    = json.loads(creds_name)[0]["cred_info"]
    ci_surname = json.loads(creds_surname)[0]["cred_info"]
    ci_gender  = json.loads(creds_gender)[0]["cred_info"]

    print("→ using cred_info for name   :", ci_name)
    print("→ using cred_info for surname:", ci_surname)
    print("→ using cred_info for gender :", ci_gender)

    # build requested_creds
    requested_creds = {
        "self_attested_attributes": {},
        "requested_attributes": {
            "attr_name_referent":    {"cred_id": ci_name["referent"],    "revealed": True},
            "attr_surname_referent": {"cred_id": ci_surname["referent"], "revealed": True},
            "attr_gender_referent":  {"cred_id": ci_gender["referent"],  "revealed": True}
        },
        "requested_predicates": {}
    }
    print("→ requested_creds:", json.dumps(requested_creds, indent=2))

    schemas   = json.dumps({schema_id: json.loads(schema_json)})
    cred_defs = json.dumps({cred_def_id: json.loads(cred_def_json)})

    proof_json = await anoncreds.prover_create_proof(
        wallet_handle,
        proof_req_json,
        json.dumps(requested_creds),
        master_secret_id,
        schemas,
        cred_defs,
        "{}"
    )
    print("→ proof:", proof_json)
    return proof_json


async def verify_gender_name_proof(
    proof_req_json: str,
    proof_json: str
) -> None:
    """
    Verifier: check that the revealed gender is "F" and print name/surname.
    """
    proof = json.loads(proof_json)
    revealed = proof["requested_proof"]["revealed_attrs"]

    name    = revealed["attr_name_referent"]["raw"]
    surname = revealed["attr_surname_referent"]["raw"]
    gender  = revealed["attr_gender_referent"]["raw"]

    print(f"→ Revealed name:    {name}")
    print(f"→ Revealed surname: {surname}")
    print(f"→ Revealed gender:  {gender}")

    if gender != "F":
        raise Exception(f"Gender check failed: expected 'F', got '{gender}'")
    print("✔ Gender is female")


async def fetch_schema_and_cred_def(pool_handle, submitter_did, schema_id, cred_def_id):
    # fetch schema
    get_s_req  = await ledger.build_get_schema_request(submitter_did, schema_id)
    resp_s     = await ledger.submit_request(pool_handle, get_s_req)
    _, schema  = await ledger.parse_get_schema_response(resp_s)

    # fetch credential definition
    get_cd_req = await ledger.build_get_cred_def_request(submitter_did, cred_def_id)
    resp_cd    = await ledger.submit_request(pool_handle, get_cd_req)
    _, cd      = await ledger.parse_get_cred_def_response(resp_cd)

    return schema, cd


async def main():
    POOL_NAME    = "von-network"
    GENESIS_PATH = "config/genesis.txn"
    WALLET_ID    = "citizen_wallet"
    WALLET_KEY   = "citizen_wallet_key"
    MASTER_SECRET= "master_secret"

    # 1) Open pool
    await pool.set_protocol_version(PROTOCOL_VERSION)
    try:
        await pool.create_pool_ledger_config(
            POOL_NAME, json.dumps({"genesis_txn": GENESIS_PATH})
        )
    except IndyError:
        pass
    pool_handle = await pool.open_pool_ledger(POOL_NAME, None)
    print("✔ Opened pool:", pool_handle)

    # 2) Open Alice’s wallet
    try:
        await wallet.create_wallet(json.dumps({"id": WALLET_ID}), json.dumps({"key": WALLET_KEY}))
    except IndyError:
        pass
    w_handle = await wallet.open_wallet(json.dumps({"id": WALLET_ID}), json.dumps({"key": WALLET_KEY}))
    print("✔ Opened wallet:", w_handle)

    # 3) List credentials & auto‑extract IDs
    creds_json = await anoncreds.prover_get_credentials(w_handle, "{}")
    creds = json.loads(creds_json)
    print("→ Wallet credentials:\n", json.dumps(creds, indent=2))

    if not creds:
        raise Exception("No credentials in wallet!")

    first = creds[0]
    schema_id   = first["schema_id"]
    cred_def_id = first["cred_def_id"]
    submitter_did = schema_id.split(":", 1)[0]

    print("→ submitter_did:", submitter_did)
    print("→ schema_id:   ", schema_id)
    print("→ cred_def_id: ", cred_def_id)

    # 4) Fetch on‑ledger schema & cred‑def
    schema_json, cred_def_json = await fetch_schema_and_cred_def(
        pool_handle, submitter_did, schema_id, cred_def_id
    )

    # 5) Build a proof request for name, surname & gender
    proof_req = await build_gender_name_proof_request(schema_id)

    # 6) Alice (prover) creates the proof
    proof = await prover_create_gender_name_proof(
        w_handle, proof_req, MASTER_SECRET,
        schema_id, cred_def_id, schema_json, cred_def_json
    )

    # 7) Verifier checks the proof
    await verify_gender_name_proof(proof_req, proof)

    # Cleanup
    await wallet.close_wallet(w_handle)
    await pool.close_pool_ledger(pool_handle)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
