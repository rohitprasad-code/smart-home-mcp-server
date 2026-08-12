import tinytuya

def main():
    try:
        print("Scanning local subnet...")
        # deviceScan scans the local subnet using UDP broadcasts
        devices_found = tinytuya.deviceScan(verbose=False)
        print(f"\nScan complete. Discovered {len(devices_found)} devices:")
        for ip in devices_found:
            dev = devices_found[ip]
            name = dev.get("name", "N/A")
            dev_id = dev.get("id", "N/A")
            version = dev.get("version", "N/A")
            print(f"Device Name: {name}")
            print(f"  IP Address: {ip}")
            print(f"  Device ID : {dev_id}")
            print(f"  Version   : {version}")
    except Exception as e:
        print(f"\nScan failed with error: {str(e)}")

if __name__ == "__main__":
    main()
