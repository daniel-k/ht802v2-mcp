"""Data models for the Grandstream HT802 V2 API."""

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

    product_model: str = Field(description="Product model name, e.g. 'HT802V2'. (P89)")
    serial_number: str = Field(description="Device serial number.")
    hardware_version: str = Field(description="Hardware revision, e.g. 'V1.0A'. (P917)")
    factory_config_version: str = Field(
        description="Factory configuration version string, e.g. '9610009410A'."
    )
    program_version: str = Field(description="Program (application) firmware version. (P68)")
    boot_version: str = Field(description="Bootloader firmware version. (P69)")
    core_version: str = Field(description="Core firmware version. (P70)")
    base_version: str = Field(description="Base firmware version. (P45)")
    cpe_version: str = Field(description="CPE (TR-069) version. Empty if not provisioned.")
    uptime: str = Field(description="System uptime string, e.g. '21:06:47 up 22 days'. (P199)")
    cpu_load: str = Field(description="Current CPU load percentage, e.g. '18%'.")
    system_status: str = Field(description="System status message. Empty under normal operation.")
    mac_address: str = Field(description="Device MAC address, e.g. '00:11:22:33:44:55'. (P67)")


class NetworkStatus(BaseModel):
    """Network connectivity status from the Status > Network Status page."""

    mac_address: str = Field(description="Device MAC address.")
    ipv4_address: str = Field(
        description=(
            "IPv4 address info. May contain multiple addresses separated by whitespace, "
            "e.g. 'MANAGE -- 10.0.0.1    SERVICE -- 10.0.0.2'. (P121)"
        )
    )
    ipv6_address: str = Field(description="IPv6 address. Empty if IPv6 is not configured.")
    vpn_ipv4: str = Field(description="VPN IPv4 address. Empty if no VPN is active.")
    vpn_ipv6: str = Field(description="VPN IPv6 address. Empty if no VPN is active.")
    cable_status: str = Field(description="Ethernet cable status, e.g. 'Up 100Mbps Full'.")
    pppoe_link_up: str = Field(description="PPPoE link status, e.g. 'Disabled'. (P211)")
    nat: str = Field(description="Detected NAT type, e.g. 'Unknown NAT'. (P80)")
    certificate_type: str = Field(description="TLS certificate type in use, e.g. 'ECDSA+SHA384'.")
    system_status: str = Field(description="System status message. Empty under normal operation.")


class PortStatus(BaseModel):
    """Status of a single FXS port from the Status > Port Status page."""

    port: int = Field(description="FXS port number (1 or 2).")
    hook: str = Field(description="Hook state: 'On Hook' or 'Off Hook'.")
    sip_user_id: str = Field(
        description="SIP User ID (phone number) registered on this port. "
        "(P35 for port 1, P735 for port 2)"
    )
    registration: str = Field(
        description="SIP registration state: 'Registered', 'Not Registered', etc."
    )
    sip_port: str = Field(description="Local SIP port number, e.g. '5060'.")


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
    account_active: bool = Field(description="Whether the account is active.")
    primary_sip_server: str = Field(description="Primary SIP server URL or IP address.")
    failover_sip_server: str = Field(description="Failover SIP server.")
    prefer_primary_sip_server: ApiInt = Field(description="0=No, 1=If failover reg expires, 2=Always.")
    outbound_proxy: str = Field(description="Outbound proxy IP or domain.")
    backup_outbound_proxy: str = Field(description="Backup outbound proxy.")
    prefer_primary_outbound_proxy: bool = Field(description="Prefer primary outbound proxy.")
    from_domain: str = Field(description="Optional domain override for From header.")
    allow_dhcp_option_120: bool = Field(description="Allow DHCP option 120 to override SIP server.")
    sip_user_id: str = Field(description="SIP User ID (phone number).")
    sip_authenticate_id: str = Field(description="SIP Authenticate ID.")
    name: str = Field(description="Display name for Caller ID.")
    tel_uri: Annotated[TelURI, BeforeValidator(_to_int)] = Field(description="Tel URI mode.")
    sip_dscp: int = Field(description="Layer 3 QoS SIP DSCP value (0-63).")
    rtp_dscp: int = Field(description="Layer 3 QoS RTP DSCP value (0-63).")
    dns_mode: Annotated[DNSMode, BeforeValidator(_to_int)] = Field(description="DNS resolution mode.")
    dns_srv_failover_mode: ApiInt = Field(description="DNS SRV failover mode.")
    failback_timer: int = Field(description="Failback timer in minutes.")
    max_sip_request_retries: int = Field(description="Maximum SIP request retries.")
    register_before_dns_srv_failover: bool = Field(description="Register before DNS SRV failover.")
    primary_ip: str = Field(description="Primary IP override.")
    backup_ip_1: str = Field(description="Backup IP 1.")
    backup_ip_2: str = Field(description="Backup IP 2.")
    nat_traversal: Annotated[NATTraversal, BeforeValidator(_to_int)] = Field(description="NAT traversal mode.")
    use_nat_ip: str = Field(description="NAT IP address for SIP/SDP messages.")
    proxy_require: str = Field(description="SIP Proxy-Require header value.")


class PortSIPSettings(BaseModel):
    """SIP settings for an FXS port (Port Settings > SIP page)."""

    port: int = Field(description="FXS port number (1 or 2).")
    sip_registration: bool = Field(description="Enable SIP registration.")
    sip_transport: Annotated[SIPTransport, BeforeValidator(_to_int)] = Field(description="SIP transport protocol.")
    unregister_on_reboot: Annotated[UnregisterOnReboot, BeforeValidator(_to_int)] = Field(description="Unregister behavior on reboot.")
    outgoing_call_without_registration: bool = Field(description="Allow outgoing calls without registration.")
    register_expiration: int = Field(description="Registration expiry in minutes.")
    re_register_before_expiration: int = Field(description="Re-register before expiry in seconds.")
    registration_retry_wait: int = Field(description="Registration failure retry wait in seconds.")
    registration_retry_wait_on_403: int = Field(description="Retry wait on 403 Forbidden in seconds.")
    sip_options_notify_keep_alive: Annotated[SIPKeepAlive, BeforeValidator(_to_int)] = Field(description="SIP keep-alive method.")
    sip_options_notify_interval: int = Field(description="Keep-alive interval in seconds.")
    sip_options_notify_max_lost: int = Field(description="Max lost keep-alive messages.")
    subscribe_mwi: bool = Field(description="Subscribe for MWI.")
    local_sip_port: int = Field(description="Local SIP port.")
    use_random_sip_port: bool = Field(description="Use random SIP port.")
    support_sip_instance_id: bool = Field(description="Support SIP Instance ID.")
    sip_uri_scheme_tls: Annotated[SIPURIScheme, BeforeValidator(_to_int)] = Field(description="SIP URI scheme for TLS.")
    use_privacy_header: Annotated[OptionalOverride, BeforeValidator(_to_int)] = Field(description="Use Privacy header.")
    use_p_preferred_identity: Annotated[OptionalOverride, BeforeValidator(_to_int)] = Field(description="Use P-Preferred-Identity header.")
    sip_t1_timeout: int = Field(description="SIP T1 timeout in centiseconds (50=0.5s, 100=1s).")
    sip_t2_timeout: int = Field(description="SIP T2 timeout in centiseconds (400=4s).")
    enable_100rel: bool = Field(description="Enable 100rel (PRACK).")
    add_auth_header_on_initial_register: bool = Field(description="Add Auth header on initial REGISTER.")
    enable_session_timer: bool = Field(description="Enable SIP session timer.")
    session_expiration: int = Field(description="Session expiration in seconds (90-64800).")
    min_se: int = Field(description="Minimum session expiration in seconds (90-64800).")
    force_invite: bool = Field(description="Force INVITE for session refresh.")


class PortCodecSettings(BaseModel):
    """Codec settings for an FXS port (Port Settings > Codec page)."""

    port: int = Field(description="FXS port number (1 or 2).")
    preferred_dtmf_method_1: int = Field(description="Preferred DTMF method choice 1 (100=InAudio, 101=RFC2833, 102=SIP INFO).")
    preferred_dtmf_method_2: int = Field(description="Preferred DTMF method choice 2.")
    preferred_dtmf_method_3: int = Field(description="Preferred DTMF method choice 3.")
    force_dtmf_via_sip_info: bool = Field(description="Force DTMF via SIP INFO simultaneously.")
    dtmf_payload_type: int = Field(description="RFC2833 DTMF payload type (96-127).")
    enable_dtmf_negotiation: bool = Field(description="Enable DTMF negotiation.")
    vocoder_1: int = Field(description="Preferred vocoder 1 (codec ID, e.g. 0=PCMU, 8=PCMA, 9=G.722).")
    vocoder_2: int = Field(description="Preferred vocoder 2.")
    vocoder_3: int = Field(description="Preferred vocoder 3.")
    vocoder_4: int = Field(description="Preferred vocoder 4.")
    vocoder_5: int = Field(description="Preferred vocoder 5.")
    vocoder_6: int = Field(description="Preferred vocoder 6.")
    voice_frames_per_tx: int = Field(description="Voice frames per TX packet.")
    g723_rate: int = Field(description="G.723 encoding rate.")
    ilbc_frame_size: int = Field(description="iLBC packet frame size.")
    ilbc_payload_type: int = Field(description="iLBC payload type (96-127).")
    opus_payload_type: int = Field(description="Opus payload type (96-127).")
    silence_suppression: bool = Field(description="Enable silence suppression.")
    use_first_matching_vocoder: bool = Field(description="Use first matching vocoder in 200OK SDP.")
    fax_mode: Annotated[FaxMode, BeforeValidator(_to_int)] = Field(description="Fax mode.")
    t38_max_bit_rate: Annotated[T38MaxBitRate, BeforeValidator(_to_int)] = Field(description="T.38 max bit rate.")
    jitter_buffer_type: Annotated[JitterBufferType, BeforeValidator(_to_int)] = Field(description="Jitter buffer type.")
    jitter_buffer_length: int = Field(description="Jitter buffer length.")
    local_rtp_port: int = Field(description="Local RTP port.")
    use_random_rtp_port: bool = Field(description="Use random RTP port.")
    symmetric_rtp: bool = Field(description="Enable symmetric RTP.")
    enable_rtcp: bool = Field(description="Enable RTCP.")
    srtp_mode: ApiInt = Field(description="SRTP mode.")
    srtp_key_length: ApiInt = Field(description="SRTP cipher method/key length.")


class PortAnalogLineSettings(BaseModel):
    """Analog line settings for an FXS port (Port Settings > Analog Line page)."""

    port: int = Field(description="FXS port number (1 or 2).")
    analog_signal_line_config: int = Field(description="SLIC impedance configuration.")
    caller_id_scheme: int = Field(description="Caller ID mechanism.")
    dtmf_caller_id: int = Field(description="DTMF Caller ID setting.")
    polarity_reversal: bool = Field(description="Reverse polarity on call events.")
    loop_current_disconnect: bool = Field(description="Loop current disconnect on call termination.")
    play_busy_before_lcd: bool = Field(description="Play busy/reorder before loop current disconnect.")
    loop_current_disconnect_duration: int = Field(description="LCD duration in ms (100-10000).")
    enable_pulse_dialing: bool = Field(description="Enable pulse dialing.")
    pulse_dialing_standard: Annotated[PulseDialingStandard, BeforeValidator(_to_int)] = Field(description="Pulse dialing standard.")
    enable_hook_flash: bool = Field(description="Enable hook flash.")
    hook_flash_timing: int = Field(description="Hook flash timing in ms (40-2000).")
    on_hook_timing: int = Field(description="On-hook timing in ms (40-2000).")
    gain: int = Field(description="Audio gain setting.")
    enable_lec: bool = Field(description="Enable Line Echo Canceller.")
    ring_frequency: int = Field(description="Ring frequency in Hz.")
    ring_power: int = Field(description="Ring power setting.")
    onhook_dc_feed_current: int = Field(description="DC feed current under on-hook.")


class PortCallSettings(BaseModel):
    """Call settings for an FXS port (Port Settings > Call Settings page)."""

    port: int = Field(description="FXS port number (1 or 2).")
    offhook_auto_dial: str = Field(description="Number to dial automatically when off-hook.")
    offhook_auto_dial_delay: int = Field(description="Auto-dial delay in seconds (0-60).")
    no_key_entry_timeout: int = Field(description="Timeout for no key entry in seconds.")
    early_dial: bool = Field(description="Enable early dial.")
    dial_plan_prefix: str = Field(description="Prefix added to all outbound numbers.")
    dial_plan: str = Field(description="Dial plan rules.")
    use_hash_as_dial_key: bool = Field(description="Use # as dial key.")
    enable_hash_as_redial_key: bool = Field(description="Enable # as redial key.")
    enable_call_waiting: bool = Field(description="Enable call waiting.")
    enable_call_waiting_caller_id: bool = Field(description="Enable call waiting caller ID.")
    enable_call_waiting_tone: bool = Field(description="Enable call waiting tone.")
    send_anonymous: bool = Field(description="Send anonymous (hide caller ID).")
    anonymous_call_rejection: bool = Field(description="Reject anonymous calls.")
    outgoing_call_duration_limit: int = Field(description="Outgoing call limit in minutes (0=No Limit).")
    incoming_call_duration_limit: int = Field(description="Incoming call limit in minutes (0=No Limit).")
    enable_visual_mwi: bool = Field(description="Enable visual message waiting indicator.")
    transfer_on_conference_hangup: bool = Field(description="Transfer on conference initiator hangup.")
    ringing_transfer: bool = Field(description="Transfer when transferring party hangs up during ringback.")
    no_answer_timeout: int = Field(description="No-answer timeout in seconds (1-120).")
    send_hook_flash_event: bool = Field(description="Send hook flash as DTMF event.")
    ring_timeout: int = Field(description="Ring timeout for incoming calls in seconds (0-300).")
    caller_id_display: Annotated[CallerIDDisplay, BeforeValidator(_to_int)] = Field(description="Caller ID display mode.")
    escape_hash_in_sip_uri: bool = Field(description="Replace # with %23 in SIP URI.")


class PortAdvancedSettings(BaseModel):
    """Advanced settings for an FXS port (Port Settings > Advanced page)."""

    port: int = Field(description="FXS port number (1 or 2).")
    special_feature: int = Field(description="Server type for special requirements.")
    conference_uri: str = Field(description="Conference URI for BroadSoft N-way calling.")
    allow_sip_reset: bool = Field(description="Allow SIP reset.")
    validate_incoming_sip: bool = Field(description="Validate incoming SIP messages.")
    check_sip_user_id_incoming: bool = Field(description="Check SIP User ID for incoming INVITE.")
    authenticate_incoming_invite: bool = Field(description="Authenticate incoming INVITE.")
    allow_sip_from_proxy_only: bool = Field(description="Allow incoming SIP from proxy only.")
    authenticate_cert_domain: bool = Field(description="Authenticate server certificate domain.")
    trusted_domain_name_list: str = Field(description="Trusted domain name list for TLS.")
    authenticate_cert_chain: bool = Field(description="Authenticate server certificate chain.")


class PortCallFeatures(BaseModel):
    """Call feature star-codes for an FXS port (Port Settings > Call Features page)."""

    port: int = Field(description="FXS port number (1 or 2).")
    call_features_enabled: bool = Field(description="Enable local call features.")
    reset_call_features: bool = Field(description="Reset call features.")
    bellcore_3wc: bool = Field(description="Enable Bellcore Style 3-Way Conference.")
    dnd_feature: bool = Field(description="DND feature enabled.")
    dnd_enable_code: str = Field(description="Star code to enable DND.")
    dnd_disable_code: str = Field(description="Star code to disable DND.")
    unconditional_forward_feature: bool = Field(description="Unconditional forward feature enabled.")
    unconditional_forward_enable_code: str = Field(description="Star code to enable unconditional forward.")
    unconditional_forward_disable_code: str = Field(description="Star code to disable unconditional forward.")
    busy_forward_feature: bool = Field(description="Busy forward feature enabled.")
    busy_forward_enable_code: str = Field(description="Star code to enable busy forward.")
    busy_forward_disable_code: str = Field(description="Star code to disable busy forward.")
    delayed_forward_feature: bool = Field(description="Delayed forward feature enabled.")
    delayed_forward_enable_code: str = Field(description="Star code to enable delayed forward.")
    delayed_forward_disable_code: str = Field(description="Star code to disable delayed forward.")
    call_waiting_feature: bool = Field(description="Call waiting feature enabled.")
    call_waiting_enable_code: str = Field(description="Star code to enable call waiting.")
    call_waiting_disable_code: str = Field(description="Star code to disable call waiting.")
    blind_transfer_feature: bool = Field(description="Blind transfer feature enabled.")
    blind_transfer_code: str = Field(description="Star code for blind transfer.")
    call_return_feature: bool = Field(description="Call return feature enabled.")
    call_return_code: str = Field(description="Star code for call return.")
    direct_ip_calling_feature: bool = Field(description="Direct IP calling feature enabled.")
    direct_ip_calling_code: str = Field(description="Star code for direct IP calling.")


class PortRingToneSettings(BaseModel):
    """Ring tone settings for an FXS port (Port Settings > Ring Tone page)."""

    port: int = Field(description="FXS port number (1 or 2).")
    custom_ring_tone_1: bool = Field(description="Custom ring tone 1 enabled.")
    custom_ring_tone_1_caller: str = Field(description="Caller ID pattern for custom ring tone 1.")
    custom_ring_tone_2: bool = Field(description="Custom ring tone 2 enabled.")
    custom_ring_tone_2_caller: str = Field(description="Caller ID pattern for custom ring tone 2.")
    custom_ring_tone_3: bool = Field(description="Custom ring tone 3 enabled.")
    custom_ring_tone_3_caller: str = Field(description="Caller ID pattern for custom ring tone 3.")
    ring_cadence_1: str = Field(description="Ring cadence 1 pattern (on/off timing).")
    ring_cadence_2: str = Field(description="Ring cadence 2 pattern.")
    cw_tone_enable_1: bool = Field(description="Call waiting tone 1 enabled.")
    cw_tone_caller_1: str = Field(description="Caller ID pattern for CW tone 1.")
    cw_tone_pattern_1: str = Field(description="Call waiting tone 1 pattern (frequency/cadence).")
