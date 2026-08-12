import os
import sys
import json
import tinytuya

# Ensure src/ directory is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from smart_home_mcp.config import TuyaConfig

def main():
    # 1. Initialize configuration (loads .env)
    config = TuyaConfig()
    if not config.validate_cloud():
        print("ERROR: Cloud credentials not configured in your .env file.")
        print("Please set TUYA_API_CLIENT_ID and TUYA_API_SECRET first.")
        return

    # 2. Query Tuya Developer Cloud for keys
    print(f"Connecting to Tuya Cloud ({config.region.upper()})...")
    try:
        cloud = tinytuya.Cloud(
            apiRegion=config.region,
            apiKey=config.client_id,
            apiSecret=config.secret
        )
        cloud_devices = cloud.getdevices()
        if not isinstance(cloud_devices, list):
            print("Failed to fetch devices from cloud:", cloud_devices)
            return
    except Exception as e:
        print(f"Cloud query failed: {str(e)}")
        return

    print(f"Cloud query successful. Found {len(cloud_devices)} devices.")

    # 3. Perform a local network scan to match active IPs
    print("\nScanning local subnet to match active IP addresses...")
    local_devices = {}
    try:
        local_scan = tinytuya.deviceScan(verbose=False)
        for ip, dev in local_scan.items():
            local_devices[dev.get("id")] = {
                "ip": ip,
                "version": dev.get("version", "3.3")
            }
    except Exception as e:
        print(f"Local scan failed: {str(e)}. IPs will need to be configured manually.")

    # 4. Generate the config.json content
    formatted_devices = []
    for dev in cloud_devices:
        dev_id = dev.get("id")
        name = dev.get("name", "Unnamed Device")
        local_key = dev.get("local_key") or dev.get("key")
        category = dev.get("category", "default")
        
        # Determine device type
        dev_type = "outlet"
        if category in ["dj", "dd"] or "bulb" in name.lower() or "light" in name.lower():
            dev_type = "bulb"

        # Match IP from local scan
        ip = ""
        version = "3.3"
        if dev_id in local_devices:
            ip = local_devices[dev_id]["ip"]
            version = local_devices[dev_id]["version"]

        formatted_devices.append({
            "name": name,
            "id": dev_id,
            "ip": ip,
            "key": local_key,
            "type": dev_type,
            "ver": version
        })

    # 5. Save to config directory
    try:
        config_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config"))
        os.makedirs(config_dir, exist_ok=True)
        
        # Save as config.json, devices.json, and snapshot.json for maximum compatibility
        for filename in ["config.json", "devices.json", "snapshot.json"]:
            path = os.path.join(config_dir, filename)
            with open(path, "w") as f:
                json.dump(formatted_devices, f, indent=2)
                
        print(f"\nSUCCESS! Config files generated in: {config_dir}")
        print("Generated Configuration Summary:")
        print(json.dumps(formatted_devices, indent=2))
    except Exception as e:
        print(f"\nFailed to save configuration files: {str(e)}")

if __name__ == "__main__":
    main()
