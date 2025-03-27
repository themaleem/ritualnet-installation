#!/bin/bash

set -e  # Exit on any command failure

echo "Starting setup script..."

# Step 1: Install dependencies
echo "Updating system and installing dependencies..."
sudo apt update && sudo apt upgrade -y
sudo apt -qy install curl git jq lz4 build-essential screen
sudo apt install -y docker.io

# Step 2: Install Docker Compose
echo "Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/download/v2.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
mkdir -p $DOCKER_CONFIG/cli-plugins
curl -SL https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose
chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose

echo "Docker Compose version:"
docker compose version

# Step 3: Test Docker installation
echo "Testing Docker installation..."
docker run hello-world || echo "Docker test failed, but continuing..."

# Step 4: Clone the repository
echo "Cloning repository..."
git clone https://github.com/ritual-net/infernet-container-starter
cd infernet-container-starter || { echo "Failed to enter repo directory"; exit 1; }

# Step 5: Create a detached screen and deploy the container
echo "Creating detached screen session and running deployment..."
screen -dmS ritual bash -c "cd infernet-container-starter; project=hello-world make deploy-container; exec bash"

# Step 6: Install Python dependencies and run interactive script
echo "Installing Python dependencies..."
sudo apt install -y python3-ruamel.yaml python3-ruamel.yaml.clib

echo "Running interactive Python script..."
python3 main.py

# Step 7: Bring up necessary Docker images
echo "Bringing up necessary Docker images..."
docker compose -f deploy/docker-compose.yaml down
docker compose -f deploy/docker-compose.yaml up -d
docker ps

# Step 8: Installing Foundry and dependencies
echo "Installing Foundry..."
cd ~
mkdir -p foundry
cd foundry
curl -L https://foundry.paradigm.xyz | bash
source ~/.bashrc
foundryup

echo "Configuring Foundry..."
cd ~/infernet-container-starter/projects/hello-world/contracts
rm -rf lib/infernet-sdk
export PATH="/root/.foundry/bin:$PATH"

forge install --no-commit foundry-rs/forge-std
forge install --no-commit ritual-net/infernet-sdk

echo "Setup complete!"
