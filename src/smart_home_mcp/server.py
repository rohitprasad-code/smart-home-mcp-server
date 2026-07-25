import json
import logging
from typing import Optional, Any
from mcp.server.fastmcp import FastMCP

from smart_home_mcp.config import TuyaConfig
from smart_home_mcp.tuya_client import TuyaClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("smart-home-mcp")

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
def scan_local_network(timeout: int = 5) -> str:
    """Scan the local subnet (Wi-Fi/LAN) to auto-discover Tuya devices.
    Returns their IP address, ID, and product key if broadcasted.
    
    Args:
        timeout: The time in seconds to wait for network responses. Default is 5.
    """
    res = client.scan_local_devices(timeout=timeout)
    return json.dumps(res, indent=2)

@mcp.tool()
def scan_cloud_devices() -> str:
    """Fetch all registered Tuya devices and their Local Keys from the Tuya Developer Cloud.
    This requires TUYA_API_CLIENT_ID and TUYA_API_SECRET to be configured in the .env file.
    """
    res = client.scan_cloud_devices()
    return json.dumps(res, indent=2)

def main():
    mcp.run()

if __name__ == "__main__":
    main()
