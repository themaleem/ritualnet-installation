#!/bin/bash

set -e  # Exit on any command failure

# Color Codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'  # No Color

function print_step() {
    echo -e "${YELLOW}>>> $1${NC}"
}

function print_success() {
    echo -e "${GREEN}✔ $1${NC}"
}

function print_error() {
    echo -e "${RED}✖ $1${NC}"
}

echo -e "${YELLOW}Starting setup script...${NC}"

# Step 1: Install dependencies
print_step "Updating system and installing dependencies..."
sudo apt update && sudo apt upgrade -y
sudo apt -qy install curl git jq lz4 build-essential screen
# sudo apt install -y docker.io
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
print_success "Dependencies installed."

# Step 2: Install Docker Compose if not already installed
if command -v docker-compose &>/dev/null; then
    print_success "Docker Compose is already installed. Skipping installation."
else
    print_step "Installing Docker Compose..."
    sudo rm -f /usr/local/bin/docker-compose  # Remove previous version
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose

    DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
    mkdir -p $DOCKER_CONFIG/cli-plugins
    curl -SL https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose
    chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose

    print_success "Docker Compose installed. Version:"
    docker compose version
fi

# Step 3: Test Docker installation
print_step "Testing Docker installation..."
docker run hello-world && print_success "Docker is working!" || print_error "Docker test failed, but continuing..."

# Step 4: Clone the repository
print_step "Setting up project repository..."
if [ -d "infernet-container-starter" ]; then
    print_step "Removing existing repository..."
    rm -rf infernet-container-starter
fi
git clone https://github.com/ritual-net/infernet-container-starter
cd infernet-container-starter
print_success "Repository cloned."

# Step 5: Create a detached screen and deploy the container
# print_step "Creating detached screen session for deployment..."
# screen -dmS ritual bash -c "cd infernet-container-starter; project=hello-world make deploy-container; exec bash"
# print_success "Deployment started in screen session."
print_step "Creating detached screen session for deployment..."
SCREEN_NAME="ritual"
# screen -XS $SCREEN_NAME quit

# Start the screen session and run the command
screen -dmS $SCREEN_NAME bash -c "cd infernet-container-starter; project=hello-world make deploy-container; exec bash"

# Wait for the screen session to complete: hot fix for now
print_step "Waiting 5 seconds for deployment to finish..."
sleep 10
# print_success "Deployment completed or failed."

# Step 6: Install Python dependencies and run interactive script
print_step "Installing Python dependencies..."
sudo apt install -y python3-ruamel.yaml python3-ruamel.yaml.clib
print_success "Python dependencies installed."

print_step "Running interactive Python script to update configs..."
[ -f "ritualnet_config.py" ] && rm ritualnet_config.py
curl -L -o ritualnet_config.py https://github.com/themaleem/ritualnet-installation/raw/main/utils.py
python3 /root/ritualnet_config.py
print_success "Python configuration completed."

# Step 7: Bring up necessary Docker images safely
print_step "Bringing up necessary Docker images..."
docker compose -f deploy/docker-compose.yaml down || print_error "Failed to stop existing containers (may not exist)."
docker compose -f deploy/docker-compose.yaml up -d
print_success "Docker services started."

print_step "Checking running containers..."
docker ps

# Step 8: Installing Foundry and dependencies
print_step "Installing Foundry..."
cd ~
if [ -d "foundry" ]; then
    print_step "Removing existing Foundry installation..."
    rm -rf foundry
fi
mkdir -p foundry
cd foundry
curl -L https://foundry.paradigm.xyz | bash
# kill and restart anvil incase already running
source /root/.bashrc
pkill anvil
foundryup

print_step "Configuring Foundry..."
cd ~/infernet-container-starter/projects/hello-world/contracts
rm -rf lib/infernet-sdk
rm -rf ~/infernet-container-starter/projects/hello-world/contracts/lib/forge-std
export PATH="/root/.foundry/bin:$PATH"

forge install --no-commit foundry-rs/forge-std
forge install --no-commit ritual-net/infernet-sdk
print_success "Foundry setup completed."

echo -e "${GREEN}✔ Setup complete!${NC}"
