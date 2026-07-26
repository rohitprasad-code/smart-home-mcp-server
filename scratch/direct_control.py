import os
import sys
import time

# Ensure src/ directory is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from smart_home_mcp.config import TuyaConfig
from smart_home_mcp.tuya_client import TuyaClient

def main():
    print("==================================================")
    print("STEP 2: Testing Direct Device Local Control...")
    print("==================================================")

    # 1. Initialize configuration and client
    config = TuyaConfig()
    client = TuyaClient(config)

    # 2. Specify target device information
    device_id = "d7e3c7c23647b017d0zdlk"
    
    # We will try candidate IPs where the device might be active
    candidate_ips = ["192.168.1.6", "192.168.1.4"]
    
    device_info = config.get_device(device_id)
    if device_info:
        snapshot_ip = device_info.get("ip")
        if snapshot_ip and snapshot_ip not in candidate_ips:
            candidate_ips.insert(0, snapshot_ip)

    print(f"Targeting Device ID: {device_id}")
    print(f"Candidate IPs to try: {candidate_ips}\n")

    connected = False
    for ip in candidate_ips:
        print(f"--- Attempting direct connection to {ip} ---")
        
        # Override IP for this test execution
        if device_info:
            device_info["ip"] = ip
        else:
            # Fallback mock configuration if snapshot config doesn't exist
            config.devices = [{
                "name": "Smart Bulb 12.5 Watt",
                "id": device_id,
                "ip": ip,
                "key": "Sc.;XKaUA+*ZCg6;",
                "type": "bulb",
                "ver": "3.5"
            }]
            device_info = config.devices[0]

        # Fetch status
        status = client.get_device_status(device_id)
        if "error" not in status:
            print(f"SUCCESS! Connected to device at {ip}")
            print("Device Status Response:", status)
            connected = True
            
            # Perform a toggle test (ON -> Wait 3 seconds -> OFF)
            print("\n>>> Testing ON Command...")
            on_res = client.control_device(device_id, "turn_on")
            print("Response:", on_res)

            print("Waiting 3 seconds...")
            time.sleep(3)

            print(">>> Testing OFF Command...")
            off_res = client.control_device(device_id, "turn_off")
            print("Response:", off_res)
            break
        else:
            print(f"Could not connect to {ip}: {status.get('error')}\n")

    if not connected:
        print("FAILED to connect to any candidate IP addresses.")

if __name__ == "__main__":
    main()
