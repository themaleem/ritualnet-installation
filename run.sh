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
print_success "Dependencies installed."

# Step 2: Install Docker & Docker Compose if not already installed
install_docker_compose() {
    print_warning "Docker Compose not found. Installing Docker Compose Plugin..."
    sudo apt-get update
    sudo apt-get install -y docker-compose-plugin
    
    if docker compose version &> /dev/null; then
        print_success "Docker Compose installed. Version: $(docker compose version)"
    else
        print_error "Failed to install Docker Compose."
    fi
}

setup_docker_repository() {
    print_warning "Setting up Docker repository..."
    sudo apt-get update
    sudo apt-get install -y ca-certificates curl
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc
    
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
    https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$UBUNTU_CODENAME") stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
}

# Main Execution
if command -v docker &> /dev/null; then
    print_success "Docker is installed. Version: $(docker --version)"
    
    if docker compose version &> /dev/null; then
        print_success "Docker Compose is available. Version: $(docker compose version)"
    else
        install_docker_compose
    fi
else
    print_warning "Docker not found. Installing Docker and Docker Compose..."
    
    setup_docker_repository
    
    # Install Docker (includes Docker Compose plugin)
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    # Verify installations
    if command -v docker &> /dev/null; then
        print_success "Docker installed. Version: $(docker --version)"
    else
        print_error "Failed to install Docker."
    fi

    if ! docker compose version &> /dev/null; then
        install_docker_compose
    fi
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
print_step "Creating detached screen session for deployment..."
SCREEN_NAME="ritual"
screen -ls | grep $SCREEN_NAME | cut -d. -f1 | awk '{print $1}' | xargs -I {} screen -X -S {} quit

# Start the screen session and run the command
screen -dmS $SCREEN_NAME bash -c "cd infernet-container-starter; project=hello-world make deploy-container; exec bash"

# Wait for the screen session to complete: hot fix for now
print_step "Waiting 5 seconds for deployment to finish..."
sleep 5
print_success "Moving on..."

# Step 6: Install Python dependencies and run interactive script
print_step "Installing Python dependencies..."
sudo apt install -y python3-ruamel.yaml python3-ruamel.yaml.clib
print_success "Python dependencies installed."

print_step "Running interactive Python script to update configs..."
cd
[ -f "~/ritualnet_config.py" ] && rm ~/ritualnet_config.py
curl -L -o ritualnet_config.py https://github.com/themaleem/ritualnet-installation/raw/main/utils.py
python3 ~/ritualnet_config.py
print_success "Python configuration completed."

# Step 7: Bring up necessary Docker images safely
print_step "Bringing up necessary Docker images..."
docker compose -f ~/infernet-container-starter/deploy/docker-compose.yaml down || print_error "Failed to stop existing containers (may not exist)."
docker compose -f ~/infernet-container-starter/deploy/docker-compose.yaml up -d
print_success "Docker services started."

print_step "Checking running containers..."
docker ps

# Step 8: Installing Foundry and dependencies
print_step "Installing Foundry..."
cd ~
if [ -d "~/foundry" ]; then
    print_step "Removing existing Foundry installation..."
    rm -rf ~/foundry
fi
mkdir -p ~/foundry
cd ~/foundry
curl -L https://foundry.paradigm.xyz | bash
# Explicitly source the profile file that Foundry modifies
# Ensure foundryup is in PATH
export PATH="$HOME/.foundry/bin:$PATH"
# kill and restart anvil incase already running
pkill anvil
# Directly execute foundryup without relying on PATH
"$HOME/.foundry/bin/foundryup"

print_step "Configuring Foundry..."
cd ~/infernet-container-starter/projects/hello-world/contracts
rm -rf lib/infernet-sdk
rm -rf ~/infernet-container-starter/projects/hello-world/contracts/lib/forge-std
export PATH="/root/.foundry/bin:$PATH"

forge install --no-commit foundry-rs/forge-std
forge install --no-commit ritual-net/infernet-sdk
print_success "Foundry setup completed."

echo -e "${GREEN}✔ Setup complete!${NC}"


# step 10: Deploy Consumer Contract
docker compose -f ~/infernet-container-starter/deploy/docker-compose.yaml down
docker compose -f ~/infernet-container-starter/deploy/docker-compose.yaml up -d
docker logs infernet-node

cd ~/infernet-container-starter
project=hello-world make deploy-contracts

