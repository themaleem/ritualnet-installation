import json
import os


# files_to_update = [
#         os.path.expanduser("~/infernet-container-starter/deploy/config.json"),
#         os.path.expanduser("~/infernet-container-starter/projects/hello-world/container/config.json")
#     ]

RPC_URL = "https://mainnet.base.org/"
DEFAULT_REGISTRY_ADDRESS="0x3B1554f346DFe5c482Bb4BA31b880c1C18412170"

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

def main():
    # Define the files to update
    files_to_update = [
        os.path.expanduser("./deploy.json"),
        os.path.expanduser("./hello.json")
    ]

    private_key = input("Enter wallet private_key (prefarably a burner): ")
    registry_address = get_registry_address()

    
    print("This script will update the following configuration files: ")
    for file in files_to_update:
        print(f" - {file}")
    
    for file in files_to_update:
        if os.path.exists(file):
            update_config_file(file, private_key, registry_address)
        else:
            print(f"File not found: {file}")

if __name__ == "__main__":
    main()