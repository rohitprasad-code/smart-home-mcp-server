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

    def register_device(self, device_id: str, ip: str, key: str, name: str, dev_type: str, version: str, mapping: Optional[Dict[str, Any]] = None) -> bool:
        existing_dev = None
        for dev in self.devices:
            if dev.get("id") == device_id:
                existing_dev = dev
                break
        
        if existing_dev:
            existing_dev["ip"] = ip
            existing_dev["key"] = key
            existing_dev["name"] = name
            existing_dev["type"] = dev_type
            existing_dev["ver"] = version
            if mapping is not None:
                existing_dev["mapping"] = mapping
        else:
            new_dev = {
                "name": name,
                "id": device_id,
                "ip": ip,
                "key": key,
                "type": dev_type,
                "ver": version
            }
            if mapping is not None:
                new_dev["mapping"] = mapping
            self.devices.append(new_dev)
            
        config_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "config"))
        os.makedirs(config_dir, exist_ok=True)
        
        config_list = []
        for dev in self.devices:
            config_list.append({
                "name": dev.get("name"),
                "id": dev.get("id"),
                "ip": dev.get("ip"),
                "key": dev.get("key"),
                "type": dev.get("type", "outlet"),
                "ver": dev.get("ver", "3.3")
            })
        
        try:
            with open(os.path.join(config_dir, "config.json"), "w") as f:
                json.dump(config_list, f, indent=2)
            with open(os.path.join(config_dir, "devices.json"), "w") as f:
                json.dump(self.devices, f, indent=2)
            return True
        except Exception:
            return False

    def load_scenes(self) -> Dict[str, Any]:
        config_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "config"))
        scenes_path = os.path.join(config_dir, "scenes.json")
        if os.path.exists(scenes_path):
            try:
                with open(scenes_path, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def save_scenes(self, scenes: Dict[str, Any]) -> bool:
        config_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "config"))
        os.makedirs(config_dir, exist_ok=True)
        scenes_path = os.path.join(config_dir, "scenes.json")
        try:
            with open(scenes_path, "w") as f:
                json.dump(scenes, f, indent=2)
            return True
        except Exception:
            return False

    def validate_cloud(self) -> bool:
        return bool(self.client_id and self.secret)
