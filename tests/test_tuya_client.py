import pytest
from unittest import mock
from smart_home_mcp.config import TuyaConfig
from smart_home_mcp.tuya_client import TuyaClient

@pytest.fixture
def mock_config():
    config = TuyaConfig()
    config.devices = [
        {"name": "test_plug", "id": "plug123", "ip": "192.168.1.100", "key": "key123", "type": "outlet"},
        {"name": "test_bulb", "id": "bulb456", "ip": "192.168.1.101", "key": "key456", "type": "bulb"}
    ]
    config.client_id = "test_client"
    config.secret = "test_secret"
    return config

@mock.patch("tinytuya.OutletDevice")
def test_get_device_status_success(mock_outlet, mock_config):
    mock_dev = mock.Mock()
    mock_dev.status.return_value = {"dps": {"1": True}}
    mock_outlet.return_value = mock_dev

    client = TuyaClient(mock_config)
    status = client.get_device_status("plug123")

    mock_outlet.assert_called_once_with("plug123", "192.168.1.100", "key123")
    assert status == {"dps": {"1": True}}

@mock.patch("tinytuya.OutletDevice")
def test_control_device_turn_on(mock_outlet, mock_config):
    mock_dev = mock.Mock()
    mock_dev.turn_on.return_value = {"success": True}
    mock_outlet.return_value = mock_dev

    client = TuyaClient(mock_config)
    res = client.control_device("plug123", "turn_on")

    mock_dev.turn_on.assert_called_once()
    assert res == {"success": True}

@mock.patch("tinytuya.BulbDevice")
def test_control_bulb_set_brightness(mock_bulb, mock_config):
    mock_dev = mock.Mock()
    mock_dev.set_brightness.return_value = {"success": True}
    mock_bulb.return_value = mock_dev

    client = TuyaClient(mock_config)
    res = client.control_device("bulb456", "set_brightness", brightness=500)

    mock_dev.set_brightness.assert_called_once_with(500)
    assert res == {"success": True}

@mock.patch("tinytuya.Cloud")
def test_scan_cloud_devices_success(mock_cloud_cls, mock_config):
    mock_cloud_inst = mock.Mock()
    mock_cloud_inst.getdevices.return_value = {"result": [{"id": "cloud_dev_1"}]}
    mock_cloud_cls.return_value = mock_cloud_inst

    client = TuyaClient(mock_config)
    res = client.scan_cloud_devices()

    mock_cloud_cls.assert_called_once_with(region="us", apiKey="test_client", apiSecret="test_secret")
    assert "cloud_devices" in res
    assert res["cloud_devices"][0]["id"] == "cloud_dev_1"
