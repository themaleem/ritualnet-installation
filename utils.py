import json
import os, re,  sys

from ruamel.yaml import YAML
# from pathlib import Path

config_files = [
        os.path.expanduser("~/infernet-container-starter/deploy/config.json"),
        os.path.expanduser("~/infernet-container-starter/projects/hello-world/container/config.json")
    ]

solidity_files = [
    os.path.expanduser("~/infernet-container-starter/projects/hello-world/contracts/script/Deploy.s.sol")
]

# Makefiles
makefiles = [
    os.path.expanduser("~/infernet-container-starter/projects/hello-world/contracts/Makefile")
]

# Docker files
docker_files = [
    os.path.expanduser("~/infernet-container-starter/deploy/docker-compose.yaml")
]

NODE_VERSION = "1.4.0"
RPC_URL = "https://mainnet.base.org/"
DEFAULT_REGISTRY_ADDRESS="0x3B1554f346DFe5c482Bb4BA31b880c1C18412170"
NODE_VERSION_URL = "https://ritual.academy/nodes/setup/#:~:text=CTRL%20%2B%20X.-,Edit%20Node%20Version,-Change%20the%20node%E2%80%99s"

def get_registry_address():
    user_input = input(f"Enter registry_address [Press Enter to use default: {DEFAULT_REGISTRY_ADDRESS}]: ").strip()
    return user_input if user_input else DEFAULT_REGISTRY_ADDRESS

def update_config_file(filepath, private_key, registry_address):
    try:
        with open(filepath, 'r+') as f:
            data = json.load(f)
            chain_obj = data['chain']
            wallet_obj =  chain_obj['wallet']
            snapshot_sync = chain_obj['snapshot_sync']
            
            # Update rpc_url
            if 'chain' in data and 'rpc_url' in chain_obj:
                chain_obj['rpc_url'] = RPC_URL
            
            # Update private_key (prompt user)
            if 'chain' in data and wallet_obj and 'private_key' in wallet_obj:
                wallet_obj['private_key'] = private_key
               
            
            # Update registry_address (prompt user with default)
            if 'chain' in data and 'registry_address' in chain_obj:
                chain_obj['registry_address'] = registry_address
            
            # Update snapshot_sync values
            if 'chain' in data and 'snapshot_sync' in chain_obj:
               snapshot_sync['sleep'] = 3
               snapshot_sync['batch_size'] = 50
            
            # Update trail_head_blocks
            if 'chain' in data and 'trail_head_blocks' in chain_obj:
                chain_obj['trail_head_blocks'] = 3
            
            # Write changes back to file
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()
            
        print(f"Successfully updated {filepath}")
    except Exception as e:
        print(f"Error updating {filepath}: {str(e)}")

def update_solidity_file(filepath, registry_address):
    try:
        with open(filepath, 'r+') as f:
            content = f.read()
            
            # Find and replace the registry address
            # This pattern matches the line with address registry assignment
            pattern = r'(address registry\s*=\s*)(0x[a-fA-F0-9]+);'
            updated_content = re.sub(
                pattern,
                f'\\g<1>{registry_address};',
                content
            )
            
            # Write changes back to file
            f.seek(0)
            f.write(updated_content)
            f.truncate()
            
        print(f"Successfully updated {filepath}")
    except Exception as e:
        print(f"Error updating {filepath}: {str(e)}")

def update_makefile(filepath, private_key):
    try:
        with open(filepath, 'r+') as f:
            content = f.read()
            
            # Update sender: Pattern matches sender assignment with any spacing and optional 0x
            sender_pattern = r'^(sender\s*:=\s*)(?:0x)?[a-fA-F0-9]+'
            content = re.sub(
                sender_pattern,
                f'\\g<1>{private_key}',
                content,
                flags=re.MULTILINE
            )
        
            rpc_pattern = r'^(RPC_URL\s*:=\s*).+'
            content = re.sub(
                rpc_pattern,
                f'\\g<1>{RPC_URL}',
                content,
                flags=re.MULTILINE
            )
            
            # Write changes back to file
            f.seek(0)
            f.write(content)
            f.truncate()
            
        print(f"Successfully updated Makefile: {filepath}")
    except Exception as e:
        print(f"Error updating Makefile {filepath}: {str(e)}")


def update_node_version(filepath, image_version):
    try:
        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.indent(mapping=2, sequence=4, offset=2)  # Match common Docker Compose indentation
        
        with open(filepath, 'r') as f:
            data = yaml.load(f)
        
        if 'services' in data and 'node' in data['services']:
            data['services']['node']['image'] = image_version
        
        with open(filepath, 'w') as f:
            yaml.dump(data, f)
        
        print(f"Successfully updated bode version in: {filepath}")
    except Exception as e:
        print(f"Error updating node version {filepath}: {str(e)}")


def get_node_version():
    user_input = input(f"Visit {NODE_VERSION_URL} to get the latest Node version \n[Or press Enter to use default version: {NODE_VERSION}]: ").strip()
    return user_input if user_input else NODE_VERSION

def get_private_key():
    user_input = input("Enter wallet private_key (prefarably a burner): ").strip()
    if user_input:
        return user_input 
    else:
        print("Private Key is required for this script to continue")
        sys.exit(1)

def main():
    # Define the files to update
    config_files = [
        os.path.expanduser("~/infernet-container-starter/deploy/config.json"),
        os.path.expanduser("~/infernet-container-starter/projects/hello-world/container/config.json")
    ]

    solidity_files = [
        os.path.expanduser("~/infernet-container-starter/projects/hello-world/contracts/script/Deploy.s.sol")
    ]

    # Makefiles
    makefiles = [
        os.path.expanduser("~/infernet-container-starter/projects/hello-world/contracts/Makefile")
    ]

    # Docker files
    docker_compose_files = [
        os.path.expanduser("~/infernet-container-starter/deploy/docker-compose.yaml")
    ]
    private_key = get_private_key()
    node_version = get_node_version()
    registry_address = get_registry_address()
 
    print("This script will update the following configuration files: ")
    for file in config_files:
        print(f" - {file}")
    
    print("\nSolidity files:")
    for file in solidity_files:
        print(f" - {file}")

    print("\nMakefiles:")
    for file in makefiles:
        print(f" - {file}")

    print("\nDocker compose files:")
    for file in docker_compose_files:
        print(f" - {file}")

    for file in config_files:
        if os.path.exists(file):
            update_config_file(file, private_key, registry_address)
        else:
            print(f"Config file not found: {file}")

    for file in solidity_files:
        if os.path.exists(file):
            update_solidity_file(file, registry_address)
        else:
            print(f"Solidity file not found: {file}")
    
    for file in makefiles:
        if os.path.exists(file):
            update_makefile(file, private_key)
        else:
            print(f"Solidity file not found: {file}")

   
    for file in docker_compose_files:
        if os.path.exists(file):
            update_node_version(file, f"ritualnetwork/infernet-node:{node_version}")
        else:
            print(f"Solidity file not found: {file}")


if __name__ == "__main__":
    main()