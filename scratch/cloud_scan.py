import os
import sys

# Ensure src/ directory is in the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from smart_home_mcp.config import TuyaConfig
from smart_home_mcp.tuya_client import TuyaClient

def main():
    # 1. Initialize configuration and client (loads .env automatically)
    config = TuyaConfig()
    client = TuyaClient(config)

    # 2. Validate cloud configuration
    if not config.validate_cloud():
        print("ERROR: Cloud credentials not fully configured in your .env file.")
        print("Please ensure TUYA_API_CLIENT_ID and TUYA_API_SECRET are set.")
        return

    print(f"Using Cloud Region: {config.region.upper()}")
    print(f"Using Client ID: {config.client_id}")
    print("Sending API request to Tuya Developer Platform...\n")

    # 3. Perform the cloud scan
    result = client.scan_cloud_devices()

    # 4. Display result
    if "error" in result:
        print(f"Cloud Scan Failed: {result['error']}")
    else:
        devices = result.get("cloud_devices", [])
        print(f"Scan complete. Discovered {len(devices)} devices in the cloud:")
        for dev in devices:
            name = dev.get("name", "N/A")
            dev_id = dev.get("id", "N/A")
            local_key = dev.get("local_key", "N/A")
            category = dev.get("category", "N/A")
            print(f"Device Name: {name}")
            print(f"  Device ID : {dev_id}")
            print(f"  Local Key : {local_key}")
            print(f"  Category  : {category}")

if __name__ == "__main__":
    main()
