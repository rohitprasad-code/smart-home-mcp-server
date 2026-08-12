import json
import pytest
from unittest import mock
from smart_home_mcp.server import mcp

@pytest.mark.anyio
@mock.patch("smart_home_mcp.server.client")
async def test_list_devices(mock_client):
    mock_client.get_devices.return_value = [{"name": "plug", "id": "123"}]
    
    # FastMCP tools are coroutines or standard functions. FastMCP.call_tool is async.
    content, _ = await mcp.call_tool("list_devices", {})
    assert len(content) == 1
    # Check text content of MCP response
    data = json.loads(content[0].text)
    assert "devices" in data
    assert data["devices"][0]["name"] == "plug"

@pytest.mark.anyio
@mock.patch("smart_home_mcp.server.client")
async def test_get_device_status(mock_client):
    mock_client.get_device_status.return_value = {"dps": {"1": True}}
    
    content, _ = await mcp.call_tool("get_device_status", {"device_id": "123"})
    assert len(content) == 1
    data = json.loads(content[0].text)
    assert data["dps"]["1"] is True
    mock_client.get_device_status.assert_called_once_with("123")

@pytest.mark.anyio
@mock.patch("smart_home_mcp.server.client")
async def test_control_device(mock_client):
    mock_client.control_device.return_value = {"success": True}
    
    content, _ = await mcp.call_tool("control_device", {
        "device_id": "123",
        "action": "turn_on"
    })
    assert len(content) == 1
    data = json.loads(content[0].text)
    assert data["success"] is True
    mock_client.control_device.assert_called_once_with("123", "turn_on")

@pytest.mark.anyio
@mock.patch("smart_home_mcp.server.client")
async def test_scan_local_network(mock_client):
    mock_client.scan_local_devices.return_value = {"discovered_devices": []}
    
    content, _ = await mcp.call_tool("scan_local_network", {})
    assert len(content) == 1
    data = json.loads(content[0].text)
    assert "discovered_devices" in data
    mock_client.scan_local_devices.assert_called_once_with()

@pytest.mark.anyio
@mock.patch("smart_home_mcp.server.config")
async def test_register_device(mock_config):
    mock_config.register_device.return_value = True
    content, _ = await mcp.call_tool("register_device", {
        "device_id": "123",
        "ip": "192.168.1.10",
        "key": "xyz",
        "name": "bulb",
        "dev_type": "bulb",
        "version": "3.3"
    })
    assert len(content) == 1
    data = json.loads(content[0].text)
    assert data["success"] is True
    mock_config.register_device.assert_called_once_with("123", "192.168.1.10", "xyz", "bulb", "bulb", "3.3", None)

@pytest.mark.anyio
@mock.patch("smart_home_mcp.server.config")
async def test_create_scene(mock_config):
    mock_config.load_scenes.return_value = {}
    mock_config.save_scenes.return_value = True
    content, _ = await mcp.call_tool("create_scene", {
        "scene_name": "TestScene",
        "devices_actions_json": '[{"device_id": "123", "action": "turn_on"}]'
    })
    assert len(content) == 1
    data = json.loads(content[0].text)
    assert data["success"] is True
    assert data["scene"] == "TestScene"

@pytest.mark.anyio
@mock.patch("smart_home_mcp.server.client")
@mock.patch("smart_home_mcp.server.config")
async def test_activate_scene(mock_config, mock_client):
    mock_config.load_scenes.return_value = {
        "TestScene": [{"device_id": "123", "action": "turn_on"}]
    }
    mock_client.control_device.return_value = {"success": True}
    content, _ = await mcp.call_tool("activate_scene", {
        "scene_name": "TestScene"
    })
    assert len(content) == 1
    data = json.loads(content[0].text)
    assert data["scene"] == "TestScene"
    assert data["results"][0]["result"]["success"] is True

@pytest.mark.anyio
@mock.patch("smart_home_mcp.server.client")
async def test_set_bulb_color_temp(mock_client):
    mock_client.set_bulb_color_temp.return_value = {"success": True}
    content, _ = await mcp.call_tool("set_bulb_color_temp", {
        "device_id": "123",
        "temp_value": 500
    })
    assert len(content) == 1
    data = json.loads(content[0].text)
    assert data["success"] is True
    mock_client.set_bulb_color_temp.assert_called_once_with("123", 500)

@pytest.mark.anyio
@mock.patch("smart_home_mcp.server.client")
async def test_set_bulb_hsv(mock_client):
    mock_client.set_bulb_hsv.return_value = {"success": True}
    content, _ = await mcp.call_tool("set_bulb_hsv", {
        "device_id": "123",
        "h": 360,
        "s": 1000,
        "v": 1000
    })
    assert len(content) == 1
    data = json.loads(content[0].text)
    assert data["success"] is True
    mock_client.set_bulb_hsv.assert_called_once_with("123", 360, 1000, 1000)
