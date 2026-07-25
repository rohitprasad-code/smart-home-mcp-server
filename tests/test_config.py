import os
import json
import pytest
from unittest import mock
from smart_home_mcp.config import TuyaConfig

def test_tuya_config_default_empty():
    with mock.patch.dict(os.environ, {}, clear=True):
        config = TuyaConfig()
        assert config.region == "us"
        assert config.client_id == ""
        assert config.secret == ""
        assert config.devices == []
        assert not config.validate_cloud()

def test_tuya_config_from_env():
    env_mock = {
        "TUYA_API_REGION": "eu",
        "TUYA_API_CLIENT_ID": "client123",
        "TUYA_API_SECRET": "secret456",
        "TUYA_DEVICE_ID": "dev789",
        "TUYA_DEVICES": '[{"name": "bulb", "id": "1", "ip": "10.0.0.5", "key": "abc"}]'
    }
    with mock.patch.dict(os.environ, env_mock, clear=True):
        config = TuyaConfig()
        assert config.region == "eu"
        assert config.client_id == "client123"
        assert config.secret == "secret456"
        assert config.test_device_id == "dev789"
        assert len(config.devices) == 1
        assert config.devices[0]["name"] == "bulb"
        assert config.get_device("1") is not None
        assert config.get_device("bulb") is not None
        assert config.validate_cloud()
