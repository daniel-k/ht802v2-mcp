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


# Port settings field mappings: list of (field_name, port1_param, port2_param)
_PORT_GENERAL_FIELDS: list[tuple[str, str, str]] = [
    ("account_active", "P271", "P401"),
    ("primary_sip_server", "P47", "P747"),
    ("failover_sip_server", "P967", "P987"),
    ("prefer_primary_sip_server", "P4567", "P4568"),
    ("outbound_proxy", "P48", "P748"),
    ("backup_outbound_proxy", "P2333", "P2433"),
    ("prefer_primary_outbound_proxy", "P28096", "P28097"),
    ("from_domain", "P8617", "P8618"),
    ("allow_dhcp_option_120", "P1411", "P1411"),
    ("sip_user_id", "P35", "P735"),
    ("sip_authenticate_id", "P36", "P736"),
    ("name", "P3", "P703"),
    ("tel_uri", "P63", "P763"),
    ("sip_dscp", "P5046", "P5047"),
    ("rtp_dscp", "P5050", "P5051"),
    ("dns_mode", "P103", "P702"),
    ("dns_srv_failover_mode", "P26040", "P26140"),
    ("failback_timer", "P60056", "P60156"),
    ("max_sip_request_retries", "P60055", "P60155"),
    ("register_before_dns_srv_failover", "P29095", "P29195"),
    ("primary_ip", "P2308", "P2408"),
    ("backup_ip_1", "P2309", "P2409"),
    ("backup_ip_2", "P2310", "P2410"),
    ("nat_traversal", "P52", "P730"),
    ("use_nat_ip", "P101", "P866"),
    ("proxy_require", "P197", "P792"),
]

_PORT_SIP_FIELDS: list[tuple[str, str, str]] = [
    ("sip_registration", "P31", "P731"),
    ("sip_transport", "P130", "P830"),
    ("unregister_on_reboot", "P81", "P752"),
    ("outgoing_call_without_registration", "P109", "P813"),
    ("register_expiration", "P32", "P732"),
    ("re_register_before_expiration", "P2330", "P2430"),
    ("registration_retry_wait", "P138", "P471"),
    ("registration_retry_wait_on_403", "P26002", "P26102"),
    ("sip_options_notify_keep_alive", "P2397", "P2497"),
    ("sip_options_notify_interval", "P2398", "P2498"),
    ("sip_options_notify_max_lost", "P2399", "P2499"),
    ("subscribe_mwi", "P99", "P709"),
    ("local_sip_port", "P40", "P740"),
    ("use_random_sip_port", "P20501", "P20502"),
    ("support_sip_instance_id", "P288", "P489"),
    ("sip_uri_scheme_tls", "P2329", "P2429"),
    ("use_privacy_header", "P2338", "P2438"),
    ("use_p_preferred_identity", "P2339", "P2439"),
    ("sip_t1_timeout", "P209", "P440"),
    ("sip_t2_timeout", "P250", "P441"),
    ("enable_100rel", "P272", "P435"),
    ("add_auth_header_on_initial_register", "P2359", "P2459"),
    ("enable_session_timer", "P2395", "P2495"),
    ("session_expiration", "P260", "P434"),
    ("min_se", "P261", "P427"),
    ("force_invite", "P265", "P431"),
]

_PORT_CODEC_FIELDS: list[tuple[str, str, str]] = [
    ("preferred_dtmf_method_1", "P850", "P860"),
    ("preferred_dtmf_method_2", "P851", "P861"),
    ("preferred_dtmf_method_3", "P852", "P862"),
    ("force_dtmf_via_sip_info", "P28794", "P28795"),
    ("dtmf_payload_type", "P79", "P779"),
    ("enable_dtmf_negotiation", "P4825", "P4826"),
    ("vocoder_1", "P57", "P757"),
    ("vocoder_2", "P58", "P758"),
    ("vocoder_3", "P59", "P759"),
    ("vocoder_4", "P60", "P760"),
    ("vocoder_5", "P61", "P761"),
    ("vocoder_6", "P62", "P762"),
    ("voice_frames_per_tx", "P37", "P737"),
    ("g723_rate", "P49", "P749"),
    ("ilbc_frame_size", "P97", "P705"),
    ("ilbc_payload_type", "P96", "P704"),
    ("opus_payload_type", "P2385", "P2485"),
    ("silence_suppression", "P50", "P750"),
    ("use_first_matching_vocoder", "P4363", "P4364"),
    ("fax_mode", "P228", "P710"),
    ("t38_max_bit_rate", "P28913", "P28914"),
    ("jitter_buffer_type", "P133", "P831"),
    ("jitter_buffer_length", "P132", "P832"),
    ("local_rtp_port", "P39", "P739"),
    ("use_random_rtp_port", "P20505", "P20506"),
    ("symmetric_rtp", "P291", "P460"),
    ("enable_rtcp", "P2392", "P2492"),
    ("srtp_mode", "P183", "P443"),
    ("srtp_key_length", "P2383", "P2483"),
]

_PORT_ANALOG_LINE_FIELDS: list[tuple[str, str, str]] = [
    ("analog_signal_line_config", "P854", "P864"),
    ("caller_id_scheme", "P853", "P863"),
    ("dtmf_caller_id", "P4661", "P4663"),
    ("polarity_reversal", "P205", "P865"),
    ("loop_current_disconnect", "P892", "P893"),
    ("play_busy_before_lcd", "P21925", "P21926"),
    ("loop_current_disconnect_duration", "P856", "P857"),
    ("enable_pulse_dialing", "P20521", "P20522"),
    ("pulse_dialing_standard", "P28165", "P28166"),
    ("enable_hook_flash", "P4424", "P4425"),
    ("hook_flash_timing", "P251", "P811"),
    ("on_hook_timing", "P833", "P834"),
    ("gain", "P247", "P248"),
    ("enable_lec", "P824", "P825"),
    ("ring_frequency", "P4429", "P4430"),
    ("ring_power", "P4234", "P4235"),
    ("onhook_dc_feed_current", "P28192", "P28193"),
]

_PORT_CALL_FIELDS: list[tuple[str, str, str]] = [
    ("offhook_auto_dial", "P71", "P771"),
    ("offhook_auto_dial_delay", "P4045", "P4046"),
    ("no_key_entry_timeout", "P85", "P292"),
    ("early_dial", "P29", "P729"),
    ("dial_plan_prefix", "P66", "P766"),
    ("dial_plan", "P4200", "P4201"),
    ("use_hash_as_dial_key", "P72", "P772"),
    ("enable_hash_as_redial_key", "P28147", "P28148"),
    ("enable_call_waiting", "P91", "P791"),
    ("enable_call_waiting_caller_id", "P714", "P823"),
    ("enable_call_waiting_tone", "P186", "P817"),
    ("send_anonymous", "P65", "P765"),
    ("anonymous_call_rejection", "P129", "P446"),
    ("outgoing_call_duration_limit", "P4420", "P4421"),
    ("incoming_call_duration_limit", "P28760", "P28761"),
    ("enable_visual_mwi", "P855", "P869"),
    ("transfer_on_conference_hangup", "P4560", "P4561"),
    ("ringing_transfer", "P4820", "P4821"),
    ("no_answer_timeout", "P139", "P470"),
    ("send_hook_flash_event", "P74", "P774"),
    ("ring_timeout", "P185", "P816"),
    ("caller_id_display", "P2324", "P2424"),
    ("escape_hash_in_sip_uri", "P1406", "P4895"),
]

_PORT_ADVANCED_FIELDS: list[tuple[str, str, str]] = [
    ("special_feature", "P198", "P767"),
    ("conference_uri", "P2318", "P2418"),
    ("allow_sip_reset", "P26015", "P26115"),
    ("validate_incoming_sip", "P4340", "P4341"),
    ("check_sip_user_id_incoming", "P258", "P449"),
    ("authenticate_incoming_invite", "P2346", "P2446"),
    ("allow_sip_from_proxy_only", "P243", "P743"),
    ("authenticate_cert_domain", "P2311", "P2411"),
    ("trusted_domain_name_list", "P60082", "P60182"),
    ("authenticate_cert_chain", "P2367", "P2467"),
]

_PORT_CALL_FEATURES_FIELDS: list[tuple[str, str, str]] = [
    ("call_features_enabled", "P191", "P751"),
    ("reset_call_features", "P24199", "P24399"),
    ("bellcore_3wc", "P4830", "P4831"),
    ("dnd_feature", "P24070", "P24270"),
    ("dnd_enable_code", "P24017", "P24217"),
    ("dnd_disable_code", "P24018", "P24218"),
    ("unconditional_forward_feature", "P24068", "P24268"),
    ("unconditional_forward_enable_code", "P24014", "P24214"),
    ("unconditional_forward_disable_code", "P24015", "P24215"),
    ("busy_forward_feature", "P24072", "P24272"),
    ("busy_forward_enable_code", "P24021", "P24221"),
    ("busy_forward_disable_code", "P24022", "P24222"),
    ("delayed_forward_feature", "P24073", "P24273"),
    ("delayed_forward_enable_code", "P24023", "P24223"),
    ("delayed_forward_disable_code", "P24024", "P24224"),
    ("call_waiting_feature", "P24064", "P24264"),
    ("call_waiting_enable_code", "P24009", "P24209"),
    ("call_waiting_disable_code", "P24008", "P24208"),
    ("blind_transfer_feature", "P24071", "P24271"),
    ("blind_transfer_code", "P24020", "P24220"),
    ("call_return_feature", "P24066", "P24266"),
    ("call_return_code", "P24011", "P24211"),
    ("direct_ip_calling_feature", "P24063", "P24263"),
    ("direct_ip_calling_code", "P24007", "P24207"),
]

_PORT_RING_TONE_FIELDS: list[tuple[str, str, str]] = [
    ("custom_ring_tone_1", "P870", "P880"),
    ("custom_ring_tone_1_caller", "P871", "P881"),
    ("custom_ring_tone_2", "P872", "P882"),
    ("custom_ring_tone_2_caller", "P873", "P883"),
    ("custom_ring_tone_3", "P874", "P884"),
    ("custom_ring_tone_3_caller", "P875", "P885"),
    ("ring_cadence_1", "P4010", "P4030"),
    ("ring_cadence_2", "P4011", "P4031"),
    ("cw_tone_enable_1", "P29074", "P29174"),
    ("cw_tone_caller_1", "P29077", "P29177"),
    ("cw_tone_pattern_1", "P29080", "P29180"),
]


def _port_params(fields: list[tuple[str, str, str]], port: int) -> list[str]:
    """Extract the P-parameter names for the given port from a field mapping."""
    idx = 1 if port == 1 else 2
    return [f[idx] for f in fields]


def _port_values(
    fields: list[tuple[str, str, str]], port: int, values: dict[str, str]
) -> dict[str, str]:
    """Map fetched P-parameter values back to field names."""
    idx = 1 if port == 1 else 2
    return {f[0]: values.get(f[idx], "") for f in fields}


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

    # --- port settings ---

    def _validate_port(self, port: int) -> None:
        if port not in (1, 2):
            raise HT802Error(f"Invalid port number: {port}. Must be 1 or 2.")

    async def get_port_general(self, port: int) -> PortGeneralSettings:
        """Get general settings for a port."""
        self._validate_port(port)
        values = await self.get_values(_port_params(_PORT_GENERAL_FIELDS, port))
        return PortGeneralSettings(port=port, **_port_values(_PORT_GENERAL_FIELDS, port, values))

    async def get_port_sip(self, port: int) -> PortSIPSettings:
        """Get SIP settings for a port."""
        self._validate_port(port)
        values = await self.get_values(_port_params(_PORT_SIP_FIELDS, port))
        return PortSIPSettings(port=port, **_port_values(_PORT_SIP_FIELDS, port, values))

    async def get_port_codec(self, port: int) -> PortCodecSettings:
        """Get codec settings for a port."""
        self._validate_port(port)
        values = await self.get_values(_port_params(_PORT_CODEC_FIELDS, port))
        return PortCodecSettings(port=port, **_port_values(_PORT_CODEC_FIELDS, port, values))

    async def get_port_analog_line(self, port: int) -> PortAnalogLineSettings:
        """Get analog line settings for a port."""
        self._validate_port(port)
        values = await self.get_values(_port_params(_PORT_ANALOG_LINE_FIELDS, port))
        return PortAnalogLineSettings(port=port, **_port_values(_PORT_ANALOG_LINE_FIELDS, port, values))

    async def get_port_call_settings(self, port: int) -> PortCallSettings:
        """Get call settings for a port."""
        self._validate_port(port)
        values = await self.get_values(_port_params(_PORT_CALL_FIELDS, port))
        return PortCallSettings(port=port, **_port_values(_PORT_CALL_FIELDS, port, values))

    async def get_port_advanced(self, port: int) -> PortAdvancedSettings:
        """Get advanced settings for a port."""
        self._validate_port(port)
        values = await self.get_values(_port_params(_PORT_ADVANCED_FIELDS, port))
        return PortAdvancedSettings(port=port, **_port_values(_PORT_ADVANCED_FIELDS, port, values))

    async def get_port_call_features(self, port: int) -> PortCallFeatures:
        """Get call feature star-codes for a port."""
        self._validate_port(port)
        values = await self.get_values(_port_params(_PORT_CALL_FEATURES_FIELDS, port))
        return PortCallFeatures(port=port, **_port_values(_PORT_CALL_FEATURES_FIELDS, port, values))

    async def get_port_ring_tone(self, port: int) -> PortRingToneSettings:
        """Get ring tone settings for a port."""
        self._validate_port(port)
        values = await self.get_values(_port_params(_PORT_RING_TONE_FIELDS, port))
        return PortRingToneSettings(port=port, **_port_values(_PORT_RING_TONE_FIELDS, port, values))

    async def reboot(self) -> None:
        """Reboot the device."""
        await self._authed_post("rs")
