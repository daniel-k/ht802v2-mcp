"""Data models for the Grandstream HT802 V2 API."""

from dataclasses import dataclass
from enum import IntEnum
from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, Field


def _to_int(v: Any) -> int:
    """Coerce API string values to int, treating empty string as 0."""
    if v == "" or v is None:
        return 0
    return int(v)


ApiInt = Annotated[int, BeforeValidator(_to_int)]
"""Integer that coerces from API string values (empty string becomes 0)."""


@dataclass(frozen=True, slots=True)
class P:
    """P-parameter annotation mapping a model field to device parameter(s).

    Single param (1:1 mapping):  P("P89")
    Port-dependent (1:2 mapping): P("P271", "P401")
    """

    p1: str
    p2: str | None = None


def _get_p(p: P, port: int | None) -> str:
    """Resolve a P annotation to the concrete param name for the given port."""
    if p.p2 is None or port is None or port == 1:
        return p.p1
    return p.p2


def _iter_p(model: type[BaseModel]):
    """Yield (field_name, P) pairs for all P-annotated fields in a model."""
    for name, field_info in model.model_fields.items():
        for meta in field_info.metadata:
            if isinstance(meta, P):
                yield name, meta
                break


def model_params(model: type[BaseModel], port: int | None = None) -> list[str]:
    """Extract P-parameter names from an annotated model.

    For 1:1 models, call without port.  For port-dependent models, pass port=1 or 2.
    """
    return [_get_p(p, port) for _, p in _iter_p(model)]


def model_values(
    model: type[BaseModel], values: dict[str, str], port: int | None = None,
) -> dict[str, str]:
    """Map fetched P-parameter values back to field names."""
    return {name: values.get(_get_p(p, port), "") for name, p in _iter_p(model)}


# --- Enums ---


class TelURI(IntEnum):
    DISABLED = 0
    USER_PHONE = 1
    ENABLED = 2


class DNSMode(IntEnum):
    A_RECORD = 0
    SRV = 1
    NAPTR_SRV = 2
    CONFIGURED_IP = 3


class NATTraversal(IntEnum):
    NO = 0
    STUN = 1
    KEEP_ALIVE = 2
    UPNP = 3
    AUTO = 4
    VPN = 5


class SIPTransport(IntEnum):
    UDP = 0
    TCP = 1
    TLS = 2


class UnregisterOnReboot(IntEnum):
    NO = 0
    ALL = 1
    INSTANCE = 2


class SIPKeepAlive(IntEnum):
    NO = 0
    OPTIONS = 1
    NOTIFY = 2


class SIPURIScheme(IntEnum):
    SIP = 0
    SIPS = 1


class OptionalOverride(IntEnum):
    """Used for Privacy Header and P-Preferred-Identity."""
    DEFAULT = 0
    NO = 1
    YES = 2


class FaxMode(IntEnum):
    T38 = 0
    PASS_THROUGH = 1


class T38MaxBitRate(IntEnum):
    BPS_4800 = 1
    BPS_9600 = 2
    BPS_14400 = 3


class JitterBufferType(IntEnum):
    FIXED = 0
    ADAPTIVE = 1


class PulseDialingStandard(IntEnum):
    GENERAL = 0
    SWEDISH = 1
    NEW_ZEALAND = 2


class CallerIDDisplay(IntEnum):
    AUTO = 0
    DISABLED = 1
    FROM_HEADER = 2


class SystemInfo(BaseModel):
    """Device identity, firmware versions, and runtime status from the Status > System Info page."""

    product_model: Annotated[str, P("P89")] = Field(description="Product model name, e.g. 'HT802V2'.")
    serial_number: Annotated[str, P("serial_number")] = Field(description="Device serial number.")
    hardware_version: Annotated[str, P("P917")] = Field(description="Hardware revision, e.g. 'V1.0A'.")
    factory_config_version: Annotated[str, P("tmp_fact_cfg_ver_str")] = Field(
        description="Factory configuration version string, e.g. '9610009410A'."
    )
    program_version: Annotated[str, P("P68")] = Field(description="Program (application) firmware version.")
    boot_version: Annotated[str, P("P69")] = Field(description="Bootloader firmware version.")
    core_version: Annotated[str, P("P70")] = Field(description="Core firmware version.")
    base_version: Annotated[str, P("P45")] = Field(description="Base firmware version.")
    cpe_version: Annotated[str, P("cpe_version")] = Field(description="CPE (TR-069) version. Empty if not provisioned.")
    uptime: Annotated[str, P("P199")] = Field(description="System uptime string, e.g. '21:06:47 up 22 days'.")
    cpu_load: Annotated[str, P("cpu_load")] = Field(description="Current CPU load percentage, e.g. '18%'.")
    system_status: Annotated[str, P("system_status")] = Field(description="System status message. Empty under normal operation.")
    mac_address: Annotated[str, P("P67")] = Field(description="Device MAC address, e.g. '00:11:22:33:44:55'.")


class NetworkStatus(BaseModel):
    """Network connectivity status from the Status > Network Status page."""

    mac_address: Annotated[str, P("mac_display")] = Field(description="Device MAC address.")
    ipv4_address: Annotated[str, P("P121")] = Field(
        description=(
            "IPv4 address info. May contain multiple addresses separated by whitespace, "
            "e.g. 'MANAGE -- 10.0.0.1    SERVICE -- 10.0.0.2'."
        )
    )
    ipv6_address: Annotated[str, P("ipv6_addr")] = Field(description="IPv6 address. Empty if IPv6 is not configured.")
    vpn_ipv4: Annotated[str, P("vpn_ip")] = Field(description="VPN IPv4 address. Empty if no VPN is active.")
    vpn_ipv6: Annotated[str, P("vpn_ip6")] = Field(description="VPN IPv6 address. Empty if no VPN is active.")
    cable_status: Annotated[str, P("net_cable_status")] = Field(description="Ethernet cable status, e.g. 'Up 100Mbps Full'.")
    pppoe_link_up: Annotated[str, P("P211")] = Field(description="PPPoE link status, e.g. 'Disabled'.")
    nat: Annotated[str, P("P80")] = Field(description="Detected NAT type, e.g. 'Unknown NAT'.")
    certificate_type: Annotated[str, P("cert_gen")] = Field(description="TLS certificate type in use, e.g. 'ECDSA+SHA384'.")
    system_status: Annotated[str, P("system_status")] = Field(description="System status message. Empty under normal operation.")


class PortStatus(BaseModel):
    """Status of a single FXS port from the Status > Port Status page."""

    port: int = Field(description="FXS port number (1 or 2).")
    hook: Annotated[str, P("P4901", "P4902")] = Field(description="Hook state: 'On Hook' or 'Off Hook'.")
    sip_user_id: Annotated[str, P("P35", "P735")] = Field(
        description="SIP User ID (phone number) registered on this port."
    )
    registration: Annotated[str, P("P4921", "P4922")] = Field(
        description="SIP registration state: 'Registered', 'Not Registered', etc."
    )
    sip_port: Annotated[str, P("sip_port_0", "sip_port_1")] = Field(description="Local SIP port number, e.g. '5060'.")


class BaseInfo(BaseModel):
    """Basic product identification from the api-get_system_base_info endpoint."""

    product: str = Field(description="Product model, e.g. 'HT802V2'.")
    vendor: str = Field(description="Vendor name, e.g. 'Grandstream Networks, Inc.'.")


class ApplyStatus(BaseModel):
    """Whether a reboot or configuration apply is pending."""

    status: str = Field(
        description="'0' means no pending changes. Non-zero means a reboot/apply is needed."
    )




class DeviceTime(BaseModel):
    """Current device date and time."""

    time: str = Field(description="Device time as 'YYYY-MM-DD HH:MM:SS'.")


class SystemProcessInfo(BaseModel):
    """System process and provisioning status from api-get_system_info."""

    ata_memory_kb: str = Field(description="ATA process virtual memory size in KB (vsz).")
    provision_status: str = Field(
        description="Provisioning status message, e.g. "
        "'Not running, Last status : Downloading file from url.'."
    )
    core_dump_exists: str = Field(
        description="'true' if a core dump file exists, 'false' otherwise."
    )


# --- Port Settings models ---


class PortGeneralSettings(BaseModel):
    """General settings for an FXS port (Port Settings > General page)."""

    port: int = Field(description="FXS port number (1 or 2).")
    account_active: Annotated[bool, P("P271", "P401")] = Field(description="Whether the account is active.")
    primary_sip_server: Annotated[str, P("P47", "P747")] = Field(description="Primary SIP server URL or IP address.")
    failover_sip_server: Annotated[str, P("P967", "P987")] = Field(description="Failover SIP server.")
    prefer_primary_sip_server: Annotated[ApiInt, P("P4567", "P4568")] = Field(description="0=No, 1=If failover reg expires, 2=Always.")
    outbound_proxy: Annotated[str, P("P48", "P748")] = Field(description="Outbound proxy IP or domain.")
    backup_outbound_proxy: Annotated[str, P("P2333", "P2433")] = Field(description="Backup outbound proxy.")
    prefer_primary_outbound_proxy: Annotated[bool, P("P28096", "P28097")] = Field(description="Prefer primary outbound proxy.")
    from_domain: Annotated[str, P("P8617", "P8618")] = Field(description="Optional domain override for From header.")
    allow_dhcp_option_120: Annotated[bool, P("P1411", "P1411")] = Field(description="Allow DHCP option 120 to override SIP server.")
    sip_user_id: Annotated[str, P("P35", "P735")] = Field(description="SIP User ID (phone number).")
    sip_authenticate_id: Annotated[str, P("P36", "P736")] = Field(description="SIP Authenticate ID.")
    name: Annotated[str, P("P3", "P703")] = Field(description="Display name for Caller ID.")
    tel_uri: Annotated[TelURI, P("P63", "P763"), BeforeValidator(_to_int)] = Field(description="Tel URI mode.")
    sip_dscp: Annotated[int, P("P5046", "P5047")] = Field(description="Layer 3 QoS SIP DSCP value (0-63).")
    rtp_dscp: Annotated[int, P("P5050", "P5051")] = Field(description="Layer 3 QoS RTP DSCP value (0-63).")
    dns_mode: Annotated[DNSMode, P("P103", "P702"), BeforeValidator(_to_int)] = Field(description="DNS resolution mode.")
    dns_srv_failover_mode: Annotated[ApiInt, P("P26040", "P26140")] = Field(description="DNS SRV failover mode.")
    failback_timer: Annotated[int, P("P60056", "P60156")] = Field(description="Failback timer in minutes.")
    max_sip_request_retries: Annotated[int, P("P60055", "P60155")] = Field(description="Maximum SIP request retries.")
    register_before_dns_srv_failover: Annotated[bool, P("P29095", "P29195")] = Field(description="Register before DNS SRV failover.")
    primary_ip: Annotated[str, P("P2308", "P2408")] = Field(description="Primary IP override.")
    backup_ip_1: Annotated[str, P("P2309", "P2409")] = Field(description="Backup IP 1.")
    backup_ip_2: Annotated[str, P("P2310", "P2410")] = Field(description="Backup IP 2.")
    nat_traversal: Annotated[NATTraversal, P("P52", "P730"), BeforeValidator(_to_int)] = Field(description="NAT traversal mode.")
    use_nat_ip: Annotated[str, P("P101", "P866")] = Field(description="NAT IP address for SIP/SDP messages.")
    proxy_require: Annotated[str, P("P197", "P792")] = Field(description="SIP Proxy-Require header value.")


class PortSIPSettings(BaseModel):
    """SIP settings for an FXS port (Port Settings > SIP page)."""

    port: int = Field(description="FXS port number (1 or 2).")
    sip_registration: Annotated[bool, P("P31", "P731")] = Field(description="Enable SIP registration.")
    sip_transport: Annotated[SIPTransport, P("P130", "P830"), BeforeValidator(_to_int)] = Field(description="SIP transport protocol.")
    unregister_on_reboot: Annotated[UnregisterOnReboot, P("P81", "P752"), BeforeValidator(_to_int)] = Field(description="Unregister behavior on reboot.")
    outgoing_call_without_registration: Annotated[bool, P("P109", "P813")] = Field(description="Allow outgoing calls without registration.")
    register_expiration: Annotated[int, P("P32", "P732")] = Field(description="Registration expiry in minutes.")
    re_register_before_expiration: Annotated[int, P("P2330", "P2430")] = Field(description="Re-register before expiry in seconds.")
    registration_retry_wait: Annotated[int, P("P138", "P471")] = Field(description="Registration failure retry wait in seconds.")
    registration_retry_wait_on_403: Annotated[int, P("P26002", "P26102")] = Field(description="Retry wait on 403 Forbidden in seconds.")
    sip_options_notify_keep_alive: Annotated[SIPKeepAlive, P("P2397", "P2497"), BeforeValidator(_to_int)] = Field(description="SIP keep-alive method.")
    sip_options_notify_interval: Annotated[int, P("P2398", "P2498")] = Field(description="Keep-alive interval in seconds.")
    sip_options_notify_max_lost: Annotated[int, P("P2399", "P2499")] = Field(description="Max lost keep-alive messages.")
    subscribe_mwi: Annotated[bool, P("P99", "P709")] = Field(description="Subscribe for MWI.")
    local_sip_port: Annotated[int, P("P40", "P740")] = Field(description="Local SIP port.")
    use_random_sip_port: Annotated[bool, P("P20501", "P20502")] = Field(description="Use random SIP port.")
    support_sip_instance_id: Annotated[bool, P("P288", "P489")] = Field(description="Support SIP Instance ID.")
    sip_uri_scheme_tls: Annotated[SIPURIScheme, P("P2329", "P2429"), BeforeValidator(_to_int)] = Field(description="SIP URI scheme for TLS.")
    use_privacy_header: Annotated[OptionalOverride, P("P2338", "P2438"), BeforeValidator(_to_int)] = Field(description="Use Privacy header.")
    use_p_preferred_identity: Annotated[OptionalOverride, P("P2339", "P2439"), BeforeValidator(_to_int)] = Field(description="Use P-Preferred-Identity header.")
    sip_t1_timeout: Annotated[int, P("P209", "P440")] = Field(description="SIP T1 timeout in centiseconds (50=0.5s, 100=1s).")
    sip_t2_timeout: Annotated[int, P("P250", "P441")] = Field(description="SIP T2 timeout in centiseconds (400=4s).")
    enable_100rel: Annotated[bool, P("P272", "P435")] = Field(description="Enable 100rel (PRACK).")
    add_auth_header_on_initial_register: Annotated[bool, P("P2359", "P2459")] = Field(description="Add Auth header on initial REGISTER.")
    enable_session_timer: Annotated[bool, P("P2395", "P2495")] = Field(description="Enable SIP session timer.")
    session_expiration: Annotated[int, P("P260", "P434")] = Field(description="Session expiration in seconds (90-64800).")
    min_se: Annotated[int, P("P261", "P427")] = Field(description="Minimum session expiration in seconds (90-64800).")
    force_invite: Annotated[bool, P("P265", "P431")] = Field(description="Force INVITE for session refresh.")


class PortCodecSettings(BaseModel):
    """Codec settings for an FXS port (Port Settings > Codec page)."""

    port: int = Field(description="FXS port number (1 or 2).")
    preferred_dtmf_method_1: Annotated[int, P("P850", "P860")] = Field(description="Preferred DTMF method choice 1 (100=InAudio, 101=RFC2833, 102=SIP INFO).")
    preferred_dtmf_method_2: Annotated[int, P("P851", "P861")] = Field(description="Preferred DTMF method choice 2.")
    preferred_dtmf_method_3: Annotated[int, P("P852", "P862")] = Field(description="Preferred DTMF method choice 3.")
    force_dtmf_via_sip_info: Annotated[bool, P("P28794", "P28795")] = Field(description="Force DTMF via SIP INFO simultaneously.")
    dtmf_payload_type: Annotated[int, P("P79", "P779")] = Field(description="RFC2833 DTMF payload type (96-127).")
    enable_dtmf_negotiation: Annotated[bool, P("P4825", "P4826")] = Field(description="Enable DTMF negotiation.")
    vocoder_1: Annotated[int, P("P57", "P757")] = Field(description="Preferred vocoder 1 (codec ID, e.g. 0=PCMU, 8=PCMA, 9=G.722).")
    vocoder_2: Annotated[int, P("P58", "P758")] = Field(description="Preferred vocoder 2.")
    vocoder_3: Annotated[int, P("P59", "P759")] = Field(description="Preferred vocoder 3.")
    vocoder_4: Annotated[int, P("P60", "P760")] = Field(description="Preferred vocoder 4.")
    vocoder_5: Annotated[int, P("P61", "P761")] = Field(description="Preferred vocoder 5.")
    vocoder_6: Annotated[int, P("P62", "P762")] = Field(description="Preferred vocoder 6.")
    voice_frames_per_tx: Annotated[int, P("P37", "P737")] = Field(description="Voice frames per TX packet.")
    g723_rate: Annotated[int, P("P49", "P749")] = Field(description="G.723 encoding rate.")
    ilbc_frame_size: Annotated[int, P("P97", "P705")] = Field(description="iLBC packet frame size.")
    ilbc_payload_type: Annotated[int, P("P96", "P704")] = Field(description="iLBC payload type (96-127).")
    opus_payload_type: Annotated[int, P("P2385", "P2485")] = Field(description="Opus payload type (96-127).")
    silence_suppression: Annotated[bool, P("P50", "P750")] = Field(description="Enable silence suppression.")
    use_first_matching_vocoder: Annotated[bool, P("P4363", "P4364")] = Field(description="Use first matching vocoder in 200OK SDP.")
    fax_mode: Annotated[FaxMode, P("P228", "P710"), BeforeValidator(_to_int)] = Field(description="Fax mode.")
    t38_max_bit_rate: Annotated[T38MaxBitRate, P("P28913", "P28914"), BeforeValidator(_to_int)] = Field(description="T.38 max bit rate.")
    jitter_buffer_type: Annotated[JitterBufferType, P("P133", "P831"), BeforeValidator(_to_int)] = Field(description="Jitter buffer type.")
    jitter_buffer_length: Annotated[int, P("P132", "P832")] = Field(description="Jitter buffer length.")
    local_rtp_port: Annotated[int, P("P39", "P739")] = Field(description="Local RTP port.")
    use_random_rtp_port: Annotated[bool, P("P20505", "P20506")] = Field(description="Use random RTP port.")
    symmetric_rtp: Annotated[bool, P("P291", "P460")] = Field(description="Enable symmetric RTP.")
    enable_rtcp: Annotated[bool, P("P2392", "P2492")] = Field(description="Enable RTCP.")
    srtp_mode: Annotated[ApiInt, P("P183", "P443")] = Field(description="SRTP mode.")
    srtp_key_length: Annotated[ApiInt, P("P2383", "P2483")] = Field(description="SRTP cipher method/key length.")


class PortAnalogLineSettings(BaseModel):
    """Analog line settings for an FXS port (Port Settings > Analog Line page)."""

    port: int = Field(description="FXS port number (1 or 2).")
    analog_signal_line_config: Annotated[int, P("P854", "P864")] = Field(description="SLIC impedance configuration.")
    caller_id_scheme: Annotated[int, P("P853", "P863")] = Field(description="Caller ID mechanism.")
    dtmf_caller_id: Annotated[int, P("P4661", "P4663")] = Field(description="DTMF Caller ID setting.")
    polarity_reversal: Annotated[bool, P("P205", "P865")] = Field(description="Reverse polarity on call events.")
    loop_current_disconnect: Annotated[bool, P("P892", "P893")] = Field(description="Loop current disconnect on call termination.")
    play_busy_before_lcd: Annotated[bool, P("P21925", "P21926")] = Field(description="Play busy/reorder before loop current disconnect.")
    loop_current_disconnect_duration: Annotated[int, P("P856", "P857")] = Field(description="LCD duration in ms (100-10000).")
    enable_pulse_dialing: Annotated[bool, P("P20521", "P20522")] = Field(description="Enable pulse dialing.")
    pulse_dialing_standard: Annotated[PulseDialingStandard, P("P28165", "P28166"), BeforeValidator(_to_int)] = Field(description="Pulse dialing standard.")
    enable_hook_flash: Annotated[bool, P("P4424", "P4425")] = Field(description="Enable hook flash.")
    hook_flash_timing: Annotated[int, P("P251", "P811")] = Field(description="Hook flash timing in ms (40-2000).")
    on_hook_timing: Annotated[int, P("P833", "P834")] = Field(description="On-hook timing in ms (40-2000).")
    gain: Annotated[int, P("P247", "P248")] = Field(description="Audio gain setting.")
    enable_lec: Annotated[bool, P("P824", "P825")] = Field(description="Enable Line Echo Canceller.")
    ring_frequency: Annotated[int, P("P4429", "P4430")] = Field(description="Ring frequency in Hz.")
    ring_power: Annotated[int, P("P4234", "P4235")] = Field(description="Ring power setting.")
    onhook_dc_feed_current: Annotated[int, P("P28192", "P28193")] = Field(description="DC feed current under on-hook.")


class PortCallSettings(BaseModel):
    """Call settings for an FXS port (Port Settings > Call Settings page)."""

    port: int = Field(description="FXS port number (1 or 2).")
    offhook_auto_dial: Annotated[str, P("P71", "P771")] = Field(description="Number to dial automatically when off-hook.")
    offhook_auto_dial_delay: Annotated[int, P("P4045", "P4046")] = Field(description="Auto-dial delay in seconds (0-60).")
    no_key_entry_timeout: Annotated[int, P("P85", "P292")] = Field(description="Timeout for no key entry in seconds.")
    early_dial: Annotated[bool, P("P29", "P729")] = Field(description="Enable early dial.")
    dial_plan_prefix: Annotated[str, P("P66", "P766")] = Field(description="Prefix added to all outbound numbers.")
    dial_plan: Annotated[str, P("P4200", "P4201")] = Field(description="Dial plan rules.")
    use_hash_as_dial_key: Annotated[bool, P("P72", "P772")] = Field(description="Use # as dial key.")
    enable_hash_as_redial_key: Annotated[bool, P("P28147", "P28148")] = Field(description="Enable # as redial key.")
    enable_call_waiting: Annotated[bool, P("P91", "P791")] = Field(description="Enable call waiting.")
    enable_call_waiting_caller_id: Annotated[bool, P("P714", "P823")] = Field(description="Enable call waiting caller ID.")
    enable_call_waiting_tone: Annotated[bool, P("P186", "P817")] = Field(description="Enable call waiting tone.")
    send_anonymous: Annotated[bool, P("P65", "P765")] = Field(description="Send anonymous (hide caller ID).")
    anonymous_call_rejection: Annotated[bool, P("P129", "P446")] = Field(description="Reject anonymous calls.")
    outgoing_call_duration_limit: Annotated[int, P("P4420", "P4421")] = Field(description="Outgoing call limit in minutes (0=No Limit).")
    incoming_call_duration_limit: Annotated[int, P("P28760", "P28761")] = Field(description="Incoming call limit in minutes (0=No Limit).")
    enable_visual_mwi: Annotated[bool, P("P855", "P869")] = Field(description="Enable visual message waiting indicator.")
    transfer_on_conference_hangup: Annotated[bool, P("P4560", "P4561")] = Field(description="Transfer on conference initiator hangup.")
    ringing_transfer: Annotated[bool, P("P4820", "P4821")] = Field(description="Transfer when transferring party hangs up during ringback.")
    no_answer_timeout: Annotated[int, P("P139", "P470")] = Field(description="No-answer timeout in seconds (1-120).")
    send_hook_flash_event: Annotated[bool, P("P74", "P774")] = Field(description="Send hook flash as DTMF event.")
    ring_timeout: Annotated[int, P("P185", "P816")] = Field(description="Ring timeout for incoming calls in seconds (0-300).")
    caller_id_display: Annotated[CallerIDDisplay, P("P2324", "P2424"), BeforeValidator(_to_int)] = Field(description="Caller ID display mode.")
    escape_hash_in_sip_uri: Annotated[bool, P("P1406", "P4895")] = Field(description="Replace # with %23 in SIP URI.")


class PortAdvancedSettings(BaseModel):
    """Advanced settings for an FXS port (Port Settings > Advanced page)."""

    port: int = Field(description="FXS port number (1 or 2).")
    special_feature: Annotated[int, P("P198", "P767")] = Field(description="Server type for special requirements.")
    conference_uri: Annotated[str, P("P2318", "P2418")] = Field(description="Conference URI for BroadSoft N-way calling.")
    allow_sip_reset: Annotated[bool, P("P26015", "P26115")] = Field(description="Allow SIP reset.")
    validate_incoming_sip: Annotated[bool, P("P4340", "P4341")] = Field(description="Validate incoming SIP messages.")
    check_sip_user_id_incoming: Annotated[bool, P("P258", "P449")] = Field(description="Check SIP User ID for incoming INVITE.")
    authenticate_incoming_invite: Annotated[bool, P("P2346", "P2446")] = Field(description="Authenticate incoming INVITE.")
    allow_sip_from_proxy_only: Annotated[bool, P("P243", "P743")] = Field(description="Allow incoming SIP from proxy only.")
    authenticate_cert_domain: Annotated[bool, P("P2311", "P2411")] = Field(description="Authenticate server certificate domain.")
    trusted_domain_name_list: Annotated[str, P("P60082", "P60182")] = Field(description="Trusted domain name list for TLS.")
    authenticate_cert_chain: Annotated[bool, P("P2367", "P2467")] = Field(description="Authenticate server certificate chain.")


class PortCallFeatures(BaseModel):
    """Call feature star-codes for an FXS port (Port Settings > Call Features page)."""

    port: int = Field(description="FXS port number (1 or 2).")
    call_features_enabled: Annotated[bool, P("P191", "P751")] = Field(description="Enable local call features.")
    reset_call_features: Annotated[bool, P("P24199", "P24399")] = Field(description="Reset call features.")
    bellcore_3wc: Annotated[bool, P("P4830", "P4831")] = Field(description="Enable Bellcore Style 3-Way Conference.")
    dnd_feature: Annotated[bool, P("P24070", "P24270")] = Field(description="DND feature enabled.")
    dnd_enable_code: Annotated[str, P("P24017", "P24217")] = Field(description="Star code to enable DND.")
    dnd_disable_code: Annotated[str, P("P24018", "P24218")] = Field(description="Star code to disable DND.")
    unconditional_forward_feature: Annotated[bool, P("P24068", "P24268")] = Field(description="Unconditional forward feature enabled.")
    unconditional_forward_enable_code: Annotated[str, P("P24014", "P24214")] = Field(description="Star code to enable unconditional forward.")
    unconditional_forward_disable_code: Annotated[str, P("P24015", "P24215")] = Field(description="Star code to disable unconditional forward.")
    busy_forward_feature: Annotated[bool, P("P24072", "P24272")] = Field(description="Busy forward feature enabled.")
    busy_forward_enable_code: Annotated[str, P("P24021", "P24221")] = Field(description="Star code to enable busy forward.")
    busy_forward_disable_code: Annotated[str, P("P24022", "P24222")] = Field(description="Star code to disable busy forward.")
    delayed_forward_feature: Annotated[bool, P("P24073", "P24273")] = Field(description="Delayed forward feature enabled.")
    delayed_forward_enable_code: Annotated[str, P("P24023", "P24223")] = Field(description="Star code to enable delayed forward.")
    delayed_forward_disable_code: Annotated[str, P("P24024", "P24224")] = Field(description="Star code to disable delayed forward.")
    call_waiting_feature: Annotated[bool, P("P24064", "P24264")] = Field(description="Call waiting feature enabled.")
    call_waiting_enable_code: Annotated[str, P("P24009", "P24209")] = Field(description="Star code to enable call waiting.")
    call_waiting_disable_code: Annotated[str, P("P24008", "P24208")] = Field(description="Star code to disable call waiting.")
    blind_transfer_feature: Annotated[bool, P("P24071", "P24271")] = Field(description="Blind transfer feature enabled.")
    blind_transfer_code: Annotated[str, P("P24020", "P24220")] = Field(description="Star code for blind transfer.")
    call_return_feature: Annotated[bool, P("P24066", "P24266")] = Field(description="Call return feature enabled.")
    call_return_code: Annotated[str, P("P24011", "P24211")] = Field(description="Star code for call return.")
    direct_ip_calling_feature: Annotated[bool, P("P24063", "P24263")] = Field(description="Direct IP calling feature enabled.")
    direct_ip_calling_code: Annotated[str, P("P24007", "P24207")] = Field(description="Star code for direct IP calling.")


class PortRingToneSettings(BaseModel):
    """Ring tone settings for an FXS port (Port Settings > Ring Tone page)."""

    port: int = Field(description="FXS port number (1 or 2).")
    custom_ring_tone_1: Annotated[bool, P("P870", "P880")] = Field(description="Custom ring tone 1 enabled.")
    custom_ring_tone_1_caller: Annotated[str, P("P871", "P881")] = Field(description="Caller ID pattern for custom ring tone 1.")
    custom_ring_tone_2: Annotated[bool, P("P872", "P882")] = Field(description="Custom ring tone 2 enabled.")
    custom_ring_tone_2_caller: Annotated[str, P("P873", "P883")] = Field(description="Caller ID pattern for custom ring tone 2.")
    custom_ring_tone_3: Annotated[bool, P("P874", "P884")] = Field(description="Custom ring tone 3 enabled.")
    custom_ring_tone_3_caller: Annotated[str, P("P875", "P885")] = Field(description="Caller ID pattern for custom ring tone 3.")
    ring_cadence_1: Annotated[str, P("P4010", "P4030")] = Field(description="Ring cadence 1 pattern (on/off timing).")
    ring_cadence_2: Annotated[str, P("P4011", "P4031")] = Field(description="Ring cadence 2 pattern.")
    cw_tone_enable_1: Annotated[bool, P("P29074", "P29174")] = Field(description="Call waiting tone 1 enabled.")
    cw_tone_caller_1: Annotated[str, P("P29077", "P29177")] = Field(description="Caller ID pattern for CW tone 1.")
    cw_tone_pattern_1: Annotated[str, P("P29080", "P29180")] = Field(description="Call waiting tone 1 pattern (frequency/cadence).")
