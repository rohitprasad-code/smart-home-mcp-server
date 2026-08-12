import os
import json
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

class TuyaConfig:
    def __init__(self):
        # Cloud API configs
        self.region: str = os.getenv("TUYA_API_REGION", "us").lower()
        self.client_id: str = os.getenv("TUYA_API_CLIENT_ID", "")
        self.secret: str = os.getenv("TUYA_API_SECRET", "")
        self.test_device_id: str = os.getenv("TUYA_DEVICE_ID", "")
        
        # Local devices
        self.devices: List[Dict[str, Any]] = self._parse_devices()

    def _parse_devices(self) -> List[Dict[str, Any]]:
        devices_env = os.getenv("TUYA_DEVICES", "")
        if devices_env.strip():
            try:
                parsed = json.loads(devices_env)
                if isinstance(parsed, list) and len(parsed) > 0:
                    return parsed
            except json.JSONDecodeError:
                pass
        
        # Fallback to local config directory files, root files, or neighboring lumina snapshot.json
        fallback_paths = [
            os.path.join(os.getcwd(), "config", "config.json"),
            os.path.join(os.getcwd(), "config", "devices.json"),
            os.path.join(os.getcwd(), "config", "snapshot.json"),
            os.path.join(os.getcwd(), "config.json"),
            os.path.join(os.getcwd(), "devices.json")
        ]
        for config_path in fallback_paths:
            if os.path.exists(config_path):
                try:
                    with open(config_path, "r") as f:
                        parsed = json.load(f)
                        if isinstance(parsed, list):
                            return parsed
                        elif isinstance(parsed, dict) and "devices" in parsed:
                            return parsed["devices"]
                except (json.JSONDecodeError, OSError):
                    pass
                
        return []

    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        for dev in self.devices:
            if dev.get("id") == device_id or dev.get("name") == device_id:
                return dev
        return None

    def validate_cloud(self) -> bool:
        return bool(self.client_id and self.secret)
