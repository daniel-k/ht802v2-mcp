"""HTTP client for the Grandstream HT802 V2 web API."""

import asyncio
import base64
import logging
from typing import Any

import aiohttp

from .models import (
    ApplyStatus,
    BaseInfo,
    DeviceTime,
    NetworkStatus,
    PortStatus,
    SessionInfo,
    SystemInfo,
    SystemProcessInfo,
)

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 5.0

# P-parameters for System Info page
_SYSTEM_INFO_PARAMS = [
    "P89",
    "serial_number",
    "P917",
    "tmp_fact_cfg_ver_str",
    "P68",
    "P69",
    "P70",
    "P45",
    "cpe_version",
    "P199",
    "cpu_load",
    "system_status",
]

# P-parameters for Network Status page
_NETWORK_STATUS_PARAMS = [
    "mac_display",
    "P121",
    "ipv6_addr",
    "vpn_ip",
    "vpn_ip6",
    "net_cable_status",
    "P211",
    "P80",
    "cert_gen",
    "system_status",
]

# P-parameters for Port Status (port 1 and port 2 core fields)
_PORT_STATUS_PARAMS = [
    "P4901",
    "P35",
    "P4921",
    "sip_port_0",
    "P4902",
    "P735",
    "P4922",
    "sip_port_1",
]


class HT802Error(Exception):
    pass


class AuthenticationError(HT802Error):
    pass


class SessionExpiredError(HT802Error):
    pass


class HT802Client:
    """Async client for the Grandstream HT802 V2 web API."""

    def __init__(
        self,
        host: str,
        port: int = 80,
        username: str = "admin",
        password: str = "",
        *,
        use_ssl: bool = False,
        verify_ssl: bool = False,
    ) -> None:
        scheme = "https" if use_ssl else "http"
        self._base_url = f"{scheme}://{host}:{port}"
        self._username = username
        self._password = password
        self._verify_ssl = verify_ssl
        self._session: aiohttp.ClientSession | None = None
        self._session_token: str | None = None
        self._lock = asyncio.Lock()

    # --- session lifecycle ---

    def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(ssl=self._verify_ssl if self._verify_ssl else False)
            self._session = aiohttp.ClientSession(connector=connector)
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
        self._session = None
        self._session_token = None

    # --- low-level HTTP ---

    async def _get(self, path: str, params: dict[str, str] | None = None) -> Any:
        session = self._ensure_session()
        url = f"{self._base_url}/cgi-bin/{path}"
        async with session.get(
            url, params=params, timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        ) as resp:
            resp.raise_for_status()
            return await resp.json(content_type=None)

    async def _post(self, path: str, data: dict[str, str]) -> Any:
        session = self._ensure_session()
        url = f"{self._base_url}/cgi-bin/{path}"
        async with session.post(
            url, data=data, timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        ) as resp:
            resp.raise_for_status()
            return await resp.json(content_type=None)

    async def _get_text(self, path: str, params: dict[str, str] | None = None) -> str:
        session = self._ensure_session()
        url = f"{self._base_url}/cgi-bin/{path}"
        async with session.get(
            url, params=params, timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        ) as resp:
            resp.raise_for_status()
            return await resp.text()

    # --- authentication ---

    async def authenticate(self) -> str:
        """Log in and obtain a session token. Returns the session token."""
        password_b64 = base64.b64encode(self._password.encode()).decode()
        result = await self._post(
            "dologin",
            {
                "username": self._username,
                "P2": password_b64,
            },
        )

        if result.get("response") != "success":
            raise AuthenticationError(
                f"Login failed: {result}",
            )

        body = result["body"]
        self._session_token = body["session_token"]
        logger.info("Authenticated as %s (role=%s)", self._username, body.get("role"))
        return self._session_token

    def _require_token(self) -> str:
        if self._session_token is None:
            raise SessionExpiredError("Not authenticated. Call authenticate() first.")
        return self._session_token

    # --- authed request helpers ---

    async def _authed_get(self, path: str, extra_params: dict[str, str] | None = None) -> Any:
        """GET with session token, auto re-auth on expiry."""
        async with self._lock:
            if self._session_token is None:
                await self.authenticate()
            token = self._require_token()

            params: dict[str, str] = {"session_token": token}
            if extra_params:
                params.update(extra_params)

            result = await self._get(path, params)

            # Check for session expiry and retry once
            if isinstance(result, dict) and result.get("response") == "error":
                await self.authenticate()
                token = self._require_token()
                params["session_token"] = token
                result = await self._get(path, params)

            return result

    async def _authed_post(self, path: str, extra_data: dict[str, str] | None = None) -> Any:
        """POST with session token, auto re-auth on expiry."""
        async with self._lock:
            if self._session_token is None:
                await self.authenticate()
            token = self._require_token()

            data: dict[str, str] = {"session_token": token}
            if extra_data:
                data.update(extra_data)

            result = await self._post(path, data)

            if isinstance(result, dict) and result.get("response") == "error":
                await self.authenticate()
                token = self._require_token()
                data["session_token"] = token
                result = await self._post(path, data)

            return result

    # --- reading P-parameters ---

    async def get_values(self, params: list[str]) -> dict[str, str]:
        """Read P-parameters via api.values.get. Returns param->value dict."""
        request_str = ":".join(params)
        result = await self._authed_post("api.values.get", {"request": request_str})
        if isinstance(result, dict) and result.get("response") == "success":
            return result["body"]
        raise HT802Error(f"Failed to get values: {result}")

    # --- session management ---

    async def extend_session(self) -> None:
        """Send keep-alive to extend the session."""
        await self._authed_post("api-phone_operation", {"arg": "", "cmd": "extend"})

    async def get_session_info(self) -> SessionInfo:
        """Check session validity."""
        result = await self._authed_get("api-get_sessioninfo")
        r = result["results"][0]
        return SessionInfo(
            session_timeout=r["session_timeout"],
            session_id_expired=r["session_id_expired"],
        )

    # --- system info ---

    async def get_system_info(self) -> SystemInfo:
        """Get system info (Status > System Info page)."""
        values = await self.get_values(_SYSTEM_INFO_PARAMS)
        mac_values = await self.get_values(["P67"])
        return SystemInfo(
            product_model=values.get("P89", ""),
            serial_number=values.get("serial_number", ""),
            hardware_version=values.get("P917", ""),
            factory_config_version=values.get("tmp_fact_cfg_ver_str", ""),
            program_version=values.get("P68", ""),
            boot_version=values.get("P69", ""),
            core_version=values.get("P70", ""),
            base_version=values.get("P45", ""),
            cpe_version=values.get("cpe_version", ""),
            uptime=values.get("P199", ""),
            cpu_load=values.get("cpu_load", ""),
            system_status=values.get("system_status", ""),
            mac_address=mac_values.get("P67", ""),
        )

    async def get_network_status(self) -> NetworkStatus:
        """Get network status (Status > Network Status page)."""
        values = await self.get_values(_NETWORK_STATUS_PARAMS)
        return NetworkStatus(
            mac_address=values.get("mac_display", ""),
            ipv4_address=values.get("P121", ""),
            ipv6_address=values.get("ipv6_addr", ""),
            vpn_ipv4=values.get("vpn_ip", ""),
            vpn_ipv6=values.get("vpn_ip6", ""),
            cable_status=values.get("net_cable_status", ""),
            pppoe_link_up=values.get("P211", ""),
            nat=values.get("P80", ""),
            certificate_type=values.get("cert_gen", ""),
            system_status=values.get("system_status", ""),
        )

    async def get_port_status(self) -> list[PortStatus]:
        """Get FXS port status (Status > Port Status page)."""
        values = await self.get_values(_PORT_STATUS_PARAMS)
        return [
            PortStatus(
                port=1,
                hook=values.get("P4901", ""),
                sip_user_id=values.get("P35", ""),
                registration=values.get("P4921", ""),
                sip_port=values.get("sip_port_0", ""),
            ),
            PortStatus(
                port=2,
                hook=values.get("P4902", ""),
                sip_user_id=values.get("P735", ""),
                registration=values.get("P4922", ""),
                sip_port=values.get("sip_port_1", ""),
            ),
        ]

    async def get_base_info(self) -> BaseInfo:
        """Get basic product identification."""
        result = await self._authed_post("api-get_system_base_info")
        body = result["body"]
        return BaseInfo(product=body["product"], vendor=body["vendor"])

    async def get_device_time(self) -> DeviceTime:
        """Get current device time."""
        result = await self._authed_get("api-get_time")
        return DeviceTime(time=result["body"]["time"])

    async def get_apply_status(self) -> ApplyStatus:
        """Check if a reboot/apply is pending."""
        result = await self._authed_post("api-get_apply_status")
        return ApplyStatus(status=result["body"]["status"])

    async def get_system_process_info(self) -> SystemProcessInfo:
        """Get system process info (api-get_system_info)."""
        result = await self._authed_get("api-get_system_info")
        items = result["results"]
        return SystemProcessInfo(
            ata_memory_kb=items[0].get("vsz", ""),
            provision_status=items[1].get("provision status", ""),
            core_dump_exists=items[2].get("core exist", ""),
        )

    async def reboot(self) -> None:
        """Reboot the device."""
        await self._authed_post("rs")
