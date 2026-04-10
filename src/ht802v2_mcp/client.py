"""HTTP client for the Grandstream HT802 V2 web API."""

import asyncio
import base64
import logging
from typing import Any

import aiohttp
from pydantic import BaseModel

from .models import (
    ApplyStatus,
    BaseInfo,
    DeviceTime,
    NetworkStatus,
    PortAdvancedSettings,
    PortAnalogLineSettings,
    PortCallFeatures,
    PortCallSettings,
    PortCodecSettings,
    PortGeneralSettings,
    PortRingToneSettings,
    PortSIPSettings,
    PortStatus,
    SystemInfo,
    SystemProcessInfo,
    model_params,
    model_values,
)

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 5.0


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
            cookie_jar = aiohttp.CookieJar(unsafe=True)  # Allow cookies from IP addresses
            self._session = aiohttp.ClientSession(connector=connector, cookie_jar=cookie_jar)
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

    # --- system info ---

    async def _get_model_values[T: BaseModel](self, model: type[T]) -> T:
        """Generic helper: fetch P-params for a 1:1 model and construct it."""
        values = await self.get_values(model_params(model))
        return model(**model_values(model, values))

    async def get_system_info(self) -> SystemInfo:
        """Get system info (Status > System Info page)."""
        return await self._get_model_values(SystemInfo)

    async def get_network_status(self) -> NetworkStatus:
        """Get network status (Status > Network Status page)."""
        return await self._get_model_values(NetworkStatus)

    async def get_port_status(self) -> list[PortStatus]:
        """Get FXS port status (Status > Port Status page)."""
        # PortStatus uses port-dependent P-params, so fetch both ports' params in one call
        all_params = model_params(PortStatus, port=1) + model_params(PortStatus, port=2)
        values = await self.get_values(all_params)
        return [
            PortStatus(port=1, **model_values(PortStatus, values, port=1)),
            PortStatus(port=2, **model_values(PortStatus, values, port=2)),
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

    # --- port settings ---

    def _validate_port(self, port: int) -> None:
        if port not in (1, 2):
            raise HT802Error(f"Invalid port number: {port}. Must be 1 or 2.")

    async def _get_port_settings[T: BaseModel](self, model: type[T], port: int) -> T:
        """Generic helper: fetch P-params for a port-dependent model and construct it."""
        self._validate_port(port)
        values = await self.get_values(model_params(model, port))
        return model(port=port, **model_values(model, values, port))

    async def get_port_general(self, port: int) -> PortGeneralSettings:
        return await self._get_port_settings(PortGeneralSettings, port)

    async def get_port_sip(self, port: int) -> PortSIPSettings:
        return await self._get_port_settings(PortSIPSettings, port)

    async def get_port_codec(self, port: int) -> PortCodecSettings:
        return await self._get_port_settings(PortCodecSettings, port)

    async def get_port_analog_line(self, port: int) -> PortAnalogLineSettings:
        return await self._get_port_settings(PortAnalogLineSettings, port)

    async def get_port_call_settings(self, port: int) -> PortCallSettings:
        return await self._get_port_settings(PortCallSettings, port)

    async def get_port_advanced(self, port: int) -> PortAdvancedSettings:
        return await self._get_port_settings(PortAdvancedSettings, port)

    async def get_port_call_features(self, port: int) -> PortCallFeatures:
        return await self._get_port_settings(PortCallFeatures, port)

    async def get_port_ring_tone(self, port: int) -> PortRingToneSettings:
        return await self._get_port_settings(PortRingToneSettings, port)

    async def reboot(self) -> None:
        """Reboot the device."""
        await self._authed_post("rs")
