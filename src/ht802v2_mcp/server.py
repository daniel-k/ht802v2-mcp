"""FastMCP server exposing the Grandstream HT802 V2 API as tools."""

import os

from fastmcp import FastMCP

from .client import HT802Client, HT802Error
from .models import (
    ApplyStatus,
    BaseInfo,
    DeviceTime,
    NetworkStatus,
    PortStatus,

    SystemInfo,
    SystemProcessInfo,
)

mcp = FastMCP(
    "Grandstream HT802V2",
    instructions=(
        "MCP server for managing a Grandstream HT802 V2 analog telephone adapter (ATA). "
        "The HT802V2 has 2 FXS ports for analog phones, 1 WAN Ethernet port, and is "
        "configured via P-parameters. Tools cover system info, network status, port "
        "status, and device operations."
    ),
)

_client: HT802Client | None = None


def _get_client() -> HT802Client:
    global _client
    if _client is None:
        host = os.environ.get("HT802_HOST", "192.168.1.1")
        port = int(os.environ.get("HT802_PORT", "80"))
        username = os.environ.get("HT802_USERNAME", "admin")
        password = os.environ.get("HT802_PASSWORD", "")
        use_ssl = os.environ.get("HT802_USE_SSL", "false").lower() == "true"
        verify_ssl = os.environ.get("HT802_VERIFY_SSL", "false").lower() == "true"
        _client = HT802Client(
            host=host,
            port=port,
            username=username,
            password=password,
            use_ssl=use_ssl,
            verify_ssl=verify_ssl,
        )
    return _client


def _err(e: HT802Error) -> str:
    return f"Error: {e}"


# ===================================================================
# SYSTEM INFO
# ===================================================================


@mcp.tool()
async def get_system_info() -> SystemInfo | str:
    """Get device identity and versions: model, serial, MAC, firmware versions, uptime, CPU load."""
    try:
        return await _get_client().get_system_info()
    except HT802Error as e:
        return _err(e)


@mcp.tool()
async def get_base_info() -> BaseInfo | str:
    """Get basic product identification: product model and vendor name."""
    try:
        return await _get_client().get_base_info()
    except HT802Error as e:
        return _err(e)


@mcp.tool()
async def get_network_status() -> NetworkStatus | str:
    """Get network status: IP addresses, cable status, NAT type, PPPoE, VPN, certificate."""
    try:
        return await _get_client().get_network_status()
    except HT802Error as e:
        return _err(e)


@mcp.tool()
async def get_port_status() -> list[PortStatus] | str:
    """Get FXS port status for both ports: hook state, SIP user, registration, SIP port."""
    try:
        return await _get_client().get_port_status()
    except HT802Error as e:
        return _err(e)


@mcp.tool()
async def get_device_time() -> DeviceTime | str:
    """Get current device date and time."""
    try:
        return await _get_client().get_device_time()
    except HT802Error as e:
        return _err(e)


@mcp.tool()
async def get_apply_status() -> ApplyStatus | str:
    """Check if a reboot or apply is pending. Status '0' means no pending changes."""
    try:
        return await _get_client().get_apply_status()
    except HT802Error as e:
        return _err(e)


@mcp.tool()
async def get_system_process_info() -> SystemProcessInfo | str:
    """Get system process info: ATA process memory, provisioning status, core dump status."""
    try:
        return await _get_client().get_system_process_info()
    except HT802Error as e:
        return _err(e)


@mcp.tool()
async def get_values(parameters: list[str]) -> dict[str, str] | str:
    """Read arbitrary P-parameters by name. Pass a list of parameter names like ['P30', 'P64'].

    All values are returned as strings. Useful for reading any device setting not covered
    by a dedicated tool.
    """
    try:
        return await _get_client().get_values(parameters)
    except HT802Error as e:
        return _err(e)



@mcp.tool()
async def reboot() -> str:
    """Reboot the device. The device will be unreachable for ~60 seconds after this call."""
    try:
        await _get_client().reboot()
        return "Reboot initiated. Device will be unreachable for ~60 seconds."
    except HT802Error as e:
        return _err(e)
