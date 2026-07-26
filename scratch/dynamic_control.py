import os
import sys
import time
import tinytuya

# Ensure src/ directory is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from smart_home_mcp.config import TuyaConfig
from smart_home_mcp.tuya_client import TuyaClient

def main():
    # 1. Initialize configuration and client
    config = TuyaConfig()
    client = TuyaClient(config)

    device_id = "d7e3c7c23647b017d0zdlk"
    print(f"Target Device ID: {device_id}")

    # 2. Perform local network scan
    print("\nScanning local subnet for active devices...")
    try:
        devices_found = tinytuya.deviceScan(verbose=False)
    except Exception as e:
        print(f"Subnet scan failed: {str(e)}")
        return

    # 3. Match scanned IP
    resolved_ip = None
    resolved_version = None
    for ip in devices_found:
        dev = devices_found[ip]
        if dev.get("id") == device_id:
            resolved_ip = ip
            resolved_version = dev.get("version")
            break

    if not resolved_ip:
        print(f"\nCould not dynamically locate device {device_id} on the network broadcast.")
        print("Make sure the device is powered on and connected to the same Wi-Fi subnet.")
        return

    print(f"\nSuccessfully resolved device on network:")
    print(f"  IP Address: {resolved_ip}")
    print(f"  Version   : {resolved_version}")

    # 4. Update config with dynamically resolved IP & version
    device_info = config.get_device(device_id)
    if device_info:
        device_info["ip"] = resolved_ip
        if resolved_version:
            device_info["ver"] = resolved_version
    else:
        # Fallback dynamic configuration
        config.devices = [{
            "name": "Smart Bulb 12.5 Watt",
            "id": device_id,
            "ip": resolved_ip,
            "key": "Sc.;XKaUA+*ZCg6;",
            "type": "bulb",
            "ver": resolved_version or "3.5"
        }]

    # 5. Fetch status
    print("\n--- Getting Device Status ---")
    status = client.get_device_status(device_id)
    print("Status Response:", status)

    # 6. Toggle Control Test
    if "error" not in status:
        print("\n>>> Turning Bulb ON...")
        on_res = client.control_device(device_id, "turn_on")
        print("Response:", on_res)

        print("Waiting 3 seconds...")
        time.sleep(3)

        print(">>> Turning Bulb OFF...")
        off_res = client.control_device(device_id, "turn_off")
        print("Response:", off_res)
    else:
        print("\nCould not test control because getting status failed with error:", status.get("error"))

if __name__ == "__main__":
    main()
