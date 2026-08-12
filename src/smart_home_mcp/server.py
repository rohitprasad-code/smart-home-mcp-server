import json
import logging
from typing import Optional, Any
from mcp.server.fastmcp import FastMCP

from smart_home_mcp.config import TuyaConfig
from smart_home_mcp.tuya_client import TuyaClient

# Configure logging to prevent noisy stdout/stderr logs
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("smart-home-mcp")
logger.setLevel(logging.WARNING)
logging.getLogger("tinytuya").setLevel(logging.WARNING)

# Initialize FastMCP Server
mcp = FastMCP("Smart Home")

# Initialize Config & Client
config = TuyaConfig()
client = TuyaClient(config)

@mcp.tool()
def list_devices() -> str:
    """List all configured local Tuya devices, including their IDs, IP addresses, types, and names."""
    devices = client.get_devices()
    return json.dumps({"devices": devices}, indent=2)

@mcp.tool()
def get_device_status(device_id: str) -> str:
    """Get the current real-time status (DPS values, power state, etc.) of a specific device by its name or ID.
    
    Args:
        device_id: The ID or name of the configured device (e.g. 'Living Room Plug' or 'bf8ab930...').
    """
    res = client.get_device_status(device_id)
    return json.dumps(res, indent=2)

@mcp.tool()
def control_device(
    device_id: str,
    action: str,
    brightness: Optional[int] = None,
    r: Optional[int] = None,
    g: Optional[int] = None,
    b: Optional[int] = None,
    dp: Optional[int] = None,
    value: Optional[bool] = None
) -> str:
    """Control a Tuya device locally.
    
    Args:
        device_id: The ID or name of the configured device (e.g. 'Living Room Plug').
        action: The control action to perform. Supported values: 'turn_on', 'turn_off', 'set_value', 'set_brightness', 'set_colour'.
        brightness: Brightness value for bulb (typically 1-1000 or 1-100 depending on device version).
        r: Red color component (0-255) for bulb set_colour.
        g: Green color component (0-255) for bulb set_colour.
        b: Blue color component (0-255) for bulb set_colour.
        dp: DP (Data Point) index integer for set_value action.
        value: Boolean value for set_value action (e.g. True or False to toggle switch DP).
    """
    kwargs = {}
    if brightness is not None:
        kwargs["brightness"] = brightness
    if r is not None:
        kwargs["r"] = r
    if g is not None:
        kwargs["g"] = g
    if b is not None:
        kwargs["b"] = b
    if dp is not None:
        kwargs["dp"] = dp
    if value is not None:
        kwargs["value"] = value

    res = client.control_device(device_id, action, **kwargs)
    return json.dumps(res, indent=2)

@mcp.tool()
def scan_local_network() -> str:
    """Scan the local subnet (Wi-Fi/LAN) to auto-discover Tuya devices.
    Returns their IP address, ID, and product key if broadcasted.
    """
    res = client.scan_local_devices()
    return json.dumps(res, indent=2)

@mcp.tool()
def scan_cloud_devices() -> str:
    """Fetch all registered Tuya devices and their Local Keys from the Tuya Developer Cloud.
    This requires TUYA_API_CLIENT_ID and TUYA_API_SECRET to be configured in the .env file.
    """
    res = client.scan_cloud_devices()
    return json.dumps(res, indent=2)

@mcp.tool()
def register_device(
    device_id: str,
    ip: str,
    key: str,
    name: str,
    dev_type: str,
    version: str,
    mapping_json: Optional[str] = None
) -> str:
    """Register or update a Tuya device configuration.
    
    Args:
        device_id: The ID of the device to register.
        ip: The local IP address of the device.
        key: The local key of the device.
        name: A friendly name for the device.
        dev_type: The type of the device (e.g. 'bulb' or 'outlet').
        version: Protocol version (e.g. '3.3' or '3.5').
        mapping_json: Optional JSON string of DP mappings.
    """
    mapping = None
    if mapping_json:
        try:
            mapping = json.loads(mapping_json)
        except Exception as e:
            return json.dumps({"error": f"Invalid mapping JSON: {str(e)}"}, indent=2)
            
    success = config.register_device(device_id, ip, key, name, dev_type, version, mapping)
    return json.dumps({"success": success}, indent=2)

@mcp.tool()
def create_scene(scene_name: str, devices_actions_json: str) -> str:
    """Create or update a scene with a series of actions across multiple devices.
    
    Args:
        scene_name: Name of the scene (e.g. 'Movie Night').
        devices_actions_json: JSON string of a list of actions. Example:
          '[{"device_id": "bulbid", "action": "set_brightness", "brightness": 200}, {"device_id": "plugid", "action": "turn_on"}]'
    """
    try:
        actions = json.loads(devices_actions_json)
        if not isinstance(actions, list):
            return json.dumps({"error": "devices_actions_json must be a JSON list of actions."}, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Invalid JSON format for actions: {str(e)}"}, indent=2)

    scenes = config.load_scenes()
    scenes[scene_name] = actions
    success = config.save_scenes(scenes)
    return json.dumps({"success": success, "scene": scene_name}, indent=2)

@mcp.tool()
def activate_scene(scene_name: str) -> str:
    """Activate a predefined scene, executing all of its control actions in sequence.
    
    Args:
        scene_name: The name of the scene to activate.
    """
    scenes = config.load_scenes()
    if scene_name not in scenes:
        return json.dumps({"error": f"Scene '{scene_name}' not found."}, indent=2)

    results = []
    actions = scenes[scene_name]
    for action_info in actions:
        if not isinstance(action_info, dict) or "device_id" not in action_info or "action" not in action_info:
            results.append({"error": "Invalid action format inside scene."})
            continue

        device_id = action_info["device_id"]
        action = action_info["action"]
        kwargs = {k: v for k, v in action_info.items() if k not in ["device_id", "action"]}
        res = client.control_device(device_id, action, **kwargs)
        results.append({"device_id": device_id, "action": action, "result": res})

    return json.dumps({"scene": scene_name, "results": results}, indent=2)

@mcp.tool()
def set_bulb_color_temp(device_id: str, temp_value: int) -> str:
    """Set the color temperature of a smart bulb (warm-to-cool range 0 to 1000).
    
    Args:
        device_id: The ID or name of the bulb.
        temp_value: Color temperature integer value from 0 (warm white/yellow) to 1000 (cool white/blue).
    """
    res = client.set_bulb_color_temp(device_id, temp_value)
    return json.dumps(res, indent=2)

@mcp.tool()
def set_bulb_hsv(device_id: str, h: int, s: int, v: int) -> str:
    """Set a smart bulb's color using Hue (0-360), Saturation (0-1000), and Value (0-1000) scale.
    
    Args:
        device_id: The ID or name of the bulb.
        h: Hue component integer (0-360 degrees).
        s: Saturation component integer (0-1000).
        v: Value/brightness component integer (0-1000).
    """
    res = client.set_bulb_hsv(device_id, h, s, v)
    return json.dumps(res, indent=2)

def main():
    mcp.run()

if __name__ == "__main__":
    main()
