# Hyperledger Indy with VON Network - Complete Setup Guide

# Work completed
@erdion-hoxha completed the full flow for an individual schema, including schema creation, credential generation, wallet storage, and verification.
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
