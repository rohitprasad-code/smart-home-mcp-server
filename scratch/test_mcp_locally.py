import os
import sys
import json
import asyncio

# Ensure src/ directory is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from smart_home_mcp.server import (
    list_devices,
    get_device_status,
    control_device,
    register_device,
    create_scene,
    activate_scene,
    set_bulb_color_temp,
    set_bulb_hsv
)

async def test_mcp_tools():
    target_device_id = "d705fbbfeb0eb9ceb6kgli"

    print("=== [1] Testing list_devices() ===")
    devices_res = list_devices()
    print("Devices List:\n", devices_res)

    print(f"\n=== [2] Testing get_device_status() for {target_device_id} ===")
    status_res = get_device_status(target_device_id)
    print("Status Result:\n", status_res)

    print(f"\n=== [3] Testing human-friendly DP control mapping (switch_led=True) ===")
    # Using code "switch_led" instead of integer DP 20
    turn_on_res = control_device(device_id=target_device_id, action="set_value", dp="switch_led", value=True)
    print("Turn On Result:\n", turn_on_res)

    print("\nWaiting 2 seconds...")
    await asyncio.sleep(2)

    print(f"\n=== [4] Testing set_brightness with auto DP mapping ===")
    brightness_res = control_device(device_id=target_device_id, action="set_brightness", brightness=500)
    print("Brightness Result:\n", brightness_res)

    print("\nWaiting 2 seconds...")
    await asyncio.sleep(2)

    print(f"\n=== [5] Testing set_bulb_color_temp() helper (warm color temp = 150) ===")
    temp_res = set_bulb_color_temp(device_id=target_device_id, temp_value=150)
    print("Color Temp Result:\n", temp_res)

    print("\nWaiting 2 seconds...")
    await asyncio.sleep(2)

    print(f"\n=== [6] Testing set_bulb_hsv() helper (Green HSV = 120, 1000, 800) ===")
    hsv_res = set_bulb_hsv(device_id=target_device_id, h=120, s=1000, v=800)
    print("HSV Result:\n", hsv_res)

    print("\nWaiting 2 seconds...")
    await asyncio.sleep(2)

    print(f"\n=== [7] Testing scene creation: 'Relaxation' ===")
    actions = [
        {"device_id": target_device_id, "action": "set_value", "dp": "work_mode", "value": "white"},
        {"device_id": target_device_id, "action": "set_brightness", "brightness": 200},
        {"device_id": target_device_id, "action": "turn_off"}
    ]
    scene_res = create_scene(scene_name="Relaxation", devices_actions_json=json.dumps(actions))
    print("Create Scene Result:\n", scene_res)

    print("\n=== [8] Testing scene activation: 'Relaxation' ===")
    activation_res = activate_scene(scene_name="Relaxation")
    print("Activate Scene Result:\n", activation_res)

if __name__ == "__main__":
    asyncio.run(test_mcp_tools())
