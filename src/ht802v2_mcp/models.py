"""Data models for the Grandstream HT802 V2 API."""

from pydantic import BaseModel, Field


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


class SessionInfo(BaseModel):
    """Current session validity status."""

    session_timeout: str = Field(
        description="'true' if the session has timed out, 'false' otherwise."
    )
    session_id_expired: str = Field(
        description="'true' if the session ID has expired, 'false' otherwise."
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
