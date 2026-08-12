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

    def _resolve_dp(self, device_info: Dict[str, Any], dp_ref: Any) -> Optional[int]:
        """Resolve a DP reference (which can be an integer, string digit, or a string code) to an integer DP."""
        if dp_ref is None:
            return None
        if isinstance(dp_ref, int):
            return dp_ref
        if isinstance(dp_ref, str) and dp_ref.isdigit():
            return int(dp_ref)
        if isinstance(dp_ref, str):
            mapping = device_info.get("mapping", {})
            for dp_num_str, details in mapping.items():
                if isinstance(details, dict) and details.get("code") == dp_ref:
                    try:
                        return int(dp_num_str)
                    except ValueError:
                        pass
        return None

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
                resolved_dp = self._resolve_dp(device_info, dp)
                if resolved_dp is None:
                    return {"error": f"Could not resolve DP code/identifier '{dp}'."}
                res = dev.set_value(resolved_dp, value)
            elif action == "set_brightness" and device_info.get("type") == "bulb":
                brightness = kwargs.get("brightness")
                if brightness is None:
                    return {"error": "Missing 'brightness' parameter."}
                resolved_dp = self._resolve_dp(device_info, "bright_value_v2") or self._resolve_dp(device_info, "bright_value")
                if resolved_dp:
                    res = dev.set_value(resolved_dp, brightness)
                else:
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

    def set_bulb_color_temp(self, device_id: str, temp_value: int) -> Dict[str, Any]:
        """Set color temperature (0 to 1000) for a bulb."""
        device_info = self.config.get_device(device_id)
        if not device_info:
            return {"error": f"Device {device_id} not found."}
        try:
            dev = self._get_device_instance(device_info)
            work_mode_dp = self._resolve_dp(device_info, "work_mode") or 21
            dev.set_value(work_mode_dp, "white")
            
            resolved_dp = self._resolve_dp(device_info, "temp_value_v2") or self._resolve_dp(device_info, "temp_value") or 23
            res = dev.set_value(resolved_dp, temp_value)
            return res
        except Exception as e:
            return {"error": f"Failed to set color temperature: {str(e)}"}

    def set_bulb_hsv(self, device_id: str, h: int, s: int, v: int) -> Dict[str, Any]:
        """Set bulb color using HSV values (Hue [0-360], Saturation [0-1000], Value [0-1000])."""
        device_info = self.config.get_device(device_id)
        if not device_info:
            return {"error": f"Device {device_id} not found."}
        try:
            dev = self._get_device_instance(device_info)
            work_mode_dp = self._resolve_dp(device_info, "work_mode") or 21
            dev.set_value(work_mode_dp, "colour")
            
            hsv_hex = f"{h:04x}{s:04x}{v:04x}"
            resolved_dp = self._resolve_dp(device_info, "colour_data_v2") or self._resolve_dp(device_info, "colour_data") or 24
            res = dev.set_value(resolved_dp, hsv_hex)
            return res
        except Exception as e:
            return {"error": f"Failed to set HSV color: {str(e)}"}

    def scan_local_devices(self) -> Dict[str, Any]:
        """Scan local subnet for Tuya devices."""
        try:
            devices = tinytuya.deviceScan(verbose=False)
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
            if isinstance(devices, list):
                return {"cloud_devices": devices}
            elif isinstance(devices, dict) and "Error" in devices:
                return {"error": devices["Error"]}
            return {"error": f"Cloud returned unexpected format: {devices}"}
        except Exception as e:
            return {"error": f"Cloud fetch failed: {str(e)}"}
