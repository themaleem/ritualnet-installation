import json
import os


# files_to_update = [
#         os.path.expanduser("~/infernet-container-starter/deploy/config.json"),
#         os.path.expanduser("~/infernet-container-starter/projects/hello-world/container/config.json")
#     ]

def get_user_input(prompt, default=None):
    if default:
        user_input = input(f"{prompt} [Press Enter to use default: {default}]: ").strip()
        return user_input if user_input else default
    return input(f"{prompt}: ").strip()

def update_config_file(filepath):
    try:
        with open(filepath, 'r+') as f:
            data = json.load(f)
            
            # Update rpc_url
            if 'chain' in data and 'rpc_url' in data['chain']:
                data['chain']['rpc_url'] = "https://mainnet.base.org/"
            
            # Update private_key (prompt user)
            if 'chain' in data and 'wallet' in data['chain'] and 'private_key' in data['chain']['wallet']:
                data['chain']['wallet']['private_key'] = get_user_input("Enter private_key for wallet (will be stored in plain text)", "")
            
            # Update registry_address (prompt user with default)
            if 'chain' in data and 'registry_address' in data['chain']:
                default_registry = "0x3B1554f346DFe5c482Bb4BA31b880c1C18412170"
                data['chain']['registry_address'] = get_user_input("Enter registry_address", default_registry)
            
            # Update snapshot_sync values
            if 'chain' in data and 'snapshot_sync' in data['chain']:
                data['chain']['snapshot_sync']['sleep'] = 3
                data['chain']['snapshot_sync']['batch_size'] = 50
            
            # Update trail_head_blocks
            if 'chain' in data and 'trail_head_blocks' in data['chain']:
                data['chain']['trail_head_blocks'] = 3
            
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
    
    print("This script will update the following configuration files:")
    for file in files_to_update:
        print(f" - {file}")
    
    for file in files_to_update:
        if os.path.exists(file):
            update_config_file(file)
        else:
            print(f"File not found: {file}")

if __name__ == "__main__":
    main()