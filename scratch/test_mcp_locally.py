import os
import sys
import asyncio

# Ensure src/ directory is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from smart_home_mcp.server import list_devices, get_device_status, control_device

async def test_mcp_tools():
    print("=== [1] Testing list_devices() ===")
    devices_res = list_devices()
    print("Devices List:\n", devices_res)

    target_device_id = "d705fbbfeb0eb9ceb6kgli"
    print(f"\n=== [2] Testing get_device_status() for {target_device_id} ===")
    status_res = get_device_status(target_device_id)
    print("Status Result:\n", status_res)

    print(f"\n=== [3] Testing control_device(turn_on) ===")
    turn_on_res = control_device(device_id=target_device_id, action="turn_on")
    print("Turn On Result:\n", turn_on_res)

    print("\nWaiting 2 seconds...")
    await asyncio.sleep(2)

    print(f"\n=== [4] Testing control_device(set_brightness) ===")
    print("Setting brightness to 300 (dim)...")
    dim_res = control_device(device_id=target_device_id, action="set_brightness", brightness=300)
    print("Brightness Result:\n", dim_res)

    print("\nWaiting 2 seconds...")
    await asyncio.sleep(2)

    print(f"\n=== [5] Testing control_device(set_colour) ===")
    print("Setting color to Red (255, 0, 0)...")
    color_res = control_device(device_id=target_device_id, action="set_colour", r=255, g=0, b=0)
    print("Color Result:\n", color_res)

    print("\nWaiting 2 seconds...")
    await asyncio.sleep(2)

    print(f"\n=== [6] Testing control_device(set_value) for White Mode ===")
    print("Setting work_mode back to 'white'...")
    white_mode_res = control_device(device_id=target_device_id, action="set_value", dp=21, value="white")
    print("Mode Change Result:\n", white_mode_res)

    print("\nWaiting 2 seconds...")
    await asyncio.sleep(2)

    print(f"\n=== [7] Testing control_device(turn_off) ===")
    turn_off_res = control_device(device_id=target_device_id, action="turn_off")
    print("Turn Off Result:\n", turn_off_res)

if __name__ == "__main__":
    asyncio.run(test_mcp_tools())
