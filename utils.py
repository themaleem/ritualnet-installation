import json
import os, re


# config_files = [
#         os.path.expanduser("~/infernet-container-starter/deploy/config.json"),
#         os.path.expanduser("~/infernet-container-starter/projects/hello-world/container/config.json")
#     ]

# solidity_files = [
#     os.path.expanduser("~/infernet-container-starter/projects/hello-world/contracts/script/Deploy.sol")
# ]

# Makefiles
# makefiles = [
#     os.path.expanduser("~/infernet-container-starter/projects/hello-world/contracts/Makefile")
# ]

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
        
            # Update RPC_URL if provided
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


def main():
    # Define the files to update
    config_files = [
        os.path.expanduser("./deploy.json"),
        os.path.expanduser("./hello.json")
    ]

    sol_files = [
        os.path.expanduser("./pop.sol")
    ]

    makefiles = [
        os.path.expanduser("./Makefile")
    ]

    private_key = input("Enter wallet private_key (prefarably a burner): ")
    registry_address = get_registry_address()
    print(registry_address)

    
    print("This script will update the following configuration files: ")
    for file in config_files:
        print(f" - {file}")
    
    print("\nSolidity files:")
    for file in sol_files:
        print(f" - {file}")

    print("\nMakefiles:")
    for file in makefiles:
        print(f" - {file}")
    
    for file in config_files:
        if os.path.exists(file):
            update_config_file(file, private_key, registry_address)
        else:
            print(f"Config file not found: {file}")

    for file in sol_files:
        if os.path.exists(file):
            update_solidity_file(file, registry_address)
        else:
            print(f"Solidity file not found: {file}")
    
    for file in makefiles:
        if os.path.exists(file):
            update_makefile(file, private_key)
        else:
            print(f"Solidity file not found: {file}")

if __name__ == "__main__":
    main()