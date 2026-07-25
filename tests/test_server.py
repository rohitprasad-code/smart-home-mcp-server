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
    
    content, _ = await mcp.call_tool("scan_local_network", {"maxretry": 3})
    assert len(content) == 1
    data = json.loads(content[0].text)
    assert "discovered_devices" in data
    mock_client.scan_local_devices.assert_called_once_with(maxretry=3)
