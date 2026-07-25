import logging
import tinytuya
from typing import Dict, List, Any, Optional
from smart_home_mcp.config import TuyaConfig

logger = logging.getLogger(__name__)

class TuyaClient:
    def __init__(self, config: TuyaConfig):
        self.config = config

    def _get_device_instance(self, device_info: Dict[str, Any]) -> tinytuya.Device:
        """Instantiate the correct TinyTuya device class based on type."""
        dev_type = device_info.get("type", "outlet").lower()
        # Fallback to detect bulb from name
        if "bulb" in device_info.get("name", "").lower():
            dev_type = "bulb"
            
        dev_id = device_info.get("id")
        ip = device_info.get("ip")
        local_key = device_info.get("key")
        # Snapshot configuration uses "ver" instead of "version"
        version = float(device_info.get("version", device_info.get("ver", "3.3")))

        if dev_type == "bulb":
            dev = tinytuya.BulbDevice(dev_id, ip, local_key)
        else:
            # Fallback to standard OutletDevice which works for plugs, switches, etc.
            dev = tinytuya.OutletDevice(dev_id, ip, local_key)

        dev.set_version(version)
        dev.set_socketTimeout(3)  # Fail fast
        return dev

    def get_devices(self) -> List[Dict[str, Any]]:
        """Return configured local devices."""
        return self.config.devices

    def get_device_status(self, device_id: str) -> Dict[str, Any]:
        """Fetch real-time status of a local device."""
        device_info = self.config.get_device(device_id)
        if not device_info:
            return {"error": f"Device {device_id} not found in configuration."}

        try:
            dev = self._get_device_instance(device_info)
            status = dev.status()
            if "error" in status:
                return {"error": f"Failed to get status: {status['error']}"}
            return status
        except Exception as e:
            return {"error": f"Exception connecting to device: {str(e)}"}

    def control_device(self, device_id: str, action: str, **kwargs) -> Dict[str, Any]:
        """Send a control command to a local device."""
        device_info = self.config.get_device(device_id)
        if not device_info:
            return {"error": f"Device {device_id} not found in configuration."}

        try:
            dev = self._get_device_instance(device_info)
            action = action.lower()
            
            if action == "turn_on":
                res = dev.turn_on()
            elif action == "turn_off":
                res = dev.turn_off()
            elif action == "set_value":
                dp = kwargs.get("dp")
                value = kwargs.get("value")
                if dp is None or value is None:
                    return {"error": "Missing 'dp' or 'value' parameter for set_value action."}
                res = dev.set_value(dp, value)
            elif action == "set_brightness" and device_info.get("type") == "bulb":
                brightness = kwargs.get("brightness") # 1-100 or 1-1000 depending on version
                if brightness is None:
                    return {"error": "Missing 'brightness' parameter."}
                res = dev.set_brightness(brightness)
            elif action == "set_colour" and device_info.get("type") == "bulb":
                r = kwargs.get("r", 255)
                g = kwargs.get("g", 255)
                b = kwargs.get("b", 255)
                res = dev.set_colour(r, g, b)
            else:
                return {"error": f"Unsupported action '{action}' for device type."}

            return res
        except Exception as e:
            return {"error": f"Exception controlling device: {str(e)}"}

    def scan_local_devices(self, maxretry: Optional[int] = None) -> Dict[str, Any]:
        """Scan local subnet for Tuya devices."""
        try:
            devices = tinytuya.deviceScan(verbose=False, maxretry=maxretry)
            return {"discovered_devices": list(devices.values())}
        except Exception as e:
            return {"error": f"Scan failed: {str(e)}"}

    def scan_cloud_devices(self) -> Dict[str, Any]:
        """Scan Tuya Developer Cloud for list of user devices and their local keys."""
        if not self.config.validate_cloud():
            return {"error": "Cloud credentials (client_id, secret) not configured."}

        try:
            cloud = tinytuya.Cloud(
                apiRegion=self.config.region,
                apiKey=self.config.client_id,
                apiSecret=self.config.secret
            )
            # Retrieve all devices registered to the Tuya account
            devices = cloud.getdevices()
            if isinstance(devices, dict) and "result" in devices:
                return {"cloud_devices": devices["result"]}
            return {"error": f"Cloud returned unexpected format: {devices}"}
        except Exception as e:
            return {"error": f"Cloud fetch failed: {str(e)}"}
