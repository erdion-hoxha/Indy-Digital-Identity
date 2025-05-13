# Hyperledger Indy with VON Network - Complete Setup Guide

## Full Installation Process

### Prerequisites Installation
First install these required components on your system:
- Git (version 2.20 or newer) - `sudo apt install git` on Linux/WSL2
- Docker and Docker Compose - Follow official Docker installation guides
- Python 3.8 or higher - `sudo apt install python3 python3-pip` on Linux/WSL2
- pip package manager - Comes with Python
- Windows users: Must install WSL2 with Ubuntu 20.04 for compatibility

### Network and SDK Setup
Run these commands sequentially in your terminal:

```bash
# Clone and start the VON Network
git clone https://github.com/bcgov/von-network.git
cd von-network
docker-compose up -d

# Verify network is running (wait for all containers to show "healthy")
docker-compose ps

# Install Indy SDK
git clone https://github.com/hyperledger/indy-sdk.git
cd indy-sdk

# Linux/WSL2 build:
./ci/run_docker_build.sh
sudo cp libindy/target/libindy.so /usr/local/lib/
sudo ldconfig

# macOS build:
brew install rust
python3 -m venv venv && source venv/bin/activate
pip install --upgrade pip setuptools
pip install .

# Return to project root and set up Python environment
cd ..
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env configuration
cat > .env <<EOF
POOL_NAME=von_test
ISSUER_WALLET_CONFIG='{"id":"issuer_wallet"}'
ISSUER_WALLET_CREDS='{"key":"issuer_key"}'
HOLDER_WALLET_CONFIG='{"id":"holder_wallet"}'
HOLDER_WALLET_CREDS='{"key":"holder_key"}'
VERIFIER_WALLET_CONFIG='{"id":"verifier_wallet"}'
VERIFIER_WALLET_CREDS='{"key":"verifier_key"}'
EOF
```

Fatemeh: 
After setting up the VON network and SDK, I did the following:
1. Defined the "Collegedegree" schema with the following attriutes: ["name", "surname", "student_id", "university_name", "field_of_study", "degree", "graduation_date", "gpa", "country_of_issuance"]
2. I then published this new schema to make a credential definition with `anoncreds.issuer_create_and_store_credential_def`
3. After creating and publishing the schema, I created a DID for a person. I first initilized an issuer and holder wallet and then generated the DID.
4. Finally genertaed and issued a smaple college degree credential and verified it using the schema. 


### Added Employment Schema & Sample Credential

After the basic network and SDK setup, Anshul did the following:

1. **Defined an `EmploymentCredential` schema**  
   - Attributes: `employee_name`, `employee_surname`, `employee_id`, `employer_name`, `position_title`, `department`, `start_date`, `end_date`, `employment_status`, `supervisor_name`, `city`, `state`, `country`  
   - Created it on‐ledger via `anoncreds.issuer_create_schema`

2. **Published a credential definition**  
   - Used the new schema to make a cred-def with `anoncreds.issuer_create_and_store_credential_def`

3. **Created a DID for a “person”**  
   - Initialized an issuer and a holder wallet, then generated a pair of DIDs (issuer and holder)

4. **Issued & stored a sample employment credential**  
   - Built a `cred_values` JSON for an example employee  
   - Ran `issuer_create_credential_offer`, `prover_create_credential_req`, and `issuer_create_credential` to issue and store it in the holder’s wallet

5. **Verified the credential**  
   - Simulated a verifier by pulling the proof from the holder and checking it against the schema and cred-def on the ledger

