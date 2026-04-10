# Grandstream HT802 V2 — Web API Documentation

Device: HT802V2, Firmware: 1.0.9.3, MAC: 00:11:22:33:44:55
Base URL: `http://<device-ip>`

All API endpoints are under `/cgi-bin/`. Authentication requires both a `session_token` parameter and a `session_id` cookie.

---

## Authentication

### POST `/cgi-bin/dologin`

Login and obtain a session token.

**Request:** `application/x-www-form-urlencoded`
```
username=admin&P2=<base64-encoded-password>
```

| Field      | Type   | Description                  |
|------------|--------|------------------------------|
| `username` | string | `admin`, `user`, or `viewer` |
| `P2`       | string | Base64-encoded password      |

**Response:**

The response includes both a JSON body and a `Set-Cookie` header. **Both are required** for subsequent authenticated requests.

Response header:
```
Set-Cookie: session_id=85769d9612e;
```

Response body:
```json
{
  "response": "success",
  "body": {
    "session_token": "7b1f473189441037bd9cd3d9db234b31",
    "role": "admin",
    "default_auth": "false",
    "oem_id": "0"
  }
}
```

> **Important:** The device validates sessions using the `session_id` **cookie**, not just the `session_token` parameter. Requests that include a valid `session_token` but omit the cookie will fail with `{"response": "error", "body": {}}` or `{"response": "error", "body": {"reason": "invalid session"}}`. When using `aiohttp`, the cookie jar must be created with `unsafe=True` to accept cookies from IP addresses (the default `CookieJar` silently rejects them per RFC 2965).

---

## Session Management

### POST `/cgi-bin/api-phone_operation`

Keep-alive / extend session.

**Request:** `application/x-www-form-urlencoded`
```
arg=&cmd=extend&session_token=<token>
```

**Response:**
```json
{"response": "success", "body": {"reason": "no error"}}
```

### GET `/cgi-bin/api-get_sessioninfo`

Check session validity.

**Request:** Query params: `session_token`, `_nocache_`

**Response:**
```json
{"results": [{"session_timeout": "false", "session_id_expired": "false"}]}
```

---

## System Info Endpoints

### GET `/cgi-bin/api-get_time`

**Query params:** `session_token`, `_nocache_`

**Response:**
```json
{"response": "success", "body": {"reason": "0", "time": "2026-04-10 21:06:47"}}
```

### GET `/cgi-bin/api-get_system_info`

**Query params:** `session_token`, `_nocache_`

**Response:**
```json
{
  "results": [
    {"vsz": "37248", "command": "ata"},
    {"provision status": "Not running, Last status : Downloading file from url."},
    {"core exist": "false"}
  ]
}
```

### POST `/cgi-bin/api-get_system_base_info`

Get basic product identification.

**Request:** `session_token=<token>`

**Response:**
```json
{"response": "success", "body": {"product": "HT802V2", "vendor": "Grandstream Networks, Inc."}}
```

### POST `/cgi-bin/api-get_apply_status`

Check if a reboot/apply is pending.

**Request:** `session_token=<token>`

**Response:**
```json
{"response": "success", "body": {"status": "0"}}
```
`status`: `"0"` = no pending changes

### GET `/cgi-bin/api-get_values_rule`

Get default/factory values for all P-parameters.

**Query params:** `session_token`, `_nocache_`

**Response:** Object keyed by P-parameter name, each with a `def` field:
```json
{
  "results": {
    "P8": {"def": "0"},
    "P30": {"def": "pool.ntp.org"},
    ...
  }
}
```

### GET `/cgi-bin/api-get_device_password_rules`

**Query params:** `session_token`, `_nocache_`

**Response:**
```json
{"results": [{"strictEnabled": 1, "minLength": 8, "noOfClasses": 3, "allowedClasses": 7}]}
```

---

## Device Operations

### POST `/cgi-bin/rs`

Reboot the device.

**Request:** `application/x-www-form-urlencoded`
```
session_token=<token>
```

**Response:**
```json
{"response": "success", "body": {"reason": "no error", "token": "c5ecd04d07a677283e59752e442a92da"}}
```

The response includes a new `token` value. After this call the device reboots and is
unreachable for ~60 seconds. The Reboot.js component is loaded to display a countdown.

---

## Config Download

### GET `/cgi-bin/download_cfg`

Download config as text (key=value pairs).

**Query params:** `session_token`

**Response:** `application/octet-stream`, attachment `config.txt`
```
P3=015551234567
P8=0
P9=192
...
```

### GET `/cgi-bin/download_cfg_xml`

Download config as XML.

**Query params:** `session_token`

**Response:** `application/octet-stream`, attachment XML
```xml
<?xml version="1.0" encoding="UTF-8"?>
<gs_provision version="1">
  <mac>001122334455</mac>
  <config version="1">
    <P3>015551234567</P3>
    ...
  </config>
</gs_provision>
```

---

## Reading Settings: POST `/cgi-bin/api.values.get`

This is the primary endpoint for reading device configuration. It fetches specific P-parameters (and virtual status fields) by name.

**Request:** `application/x-www-form-urlencoded`
```
request=P30%3AP64%3AP144&session_token=<token>
```
The `request` field is a colon-separated (`:`) list of P-parameter names (URL-encoded `%3A`).

**Response:**
```json
{"response": "success", "body": {"P30": "pool.ntp.org", "P64": "CET-1...", "P144": "1"}}
```

All values are returned as strings.

---

## Call Detail Records

### GET `/cgi-bin/api-get_cdr`

Returns call detail records array.

**Query params:** `session_token`, `_nocache_`

**Response:** Array of CDR objects:
```json
[
  {
    "userId": "...",
    "toNumber": "...",
    "fromNumber": "...",
    "startTime": "...",
    "startTalkTime": "...",
    "endTime": "...",
    "duration": "...",
    "state": "...",
    "direction": "..."
  }
]
```

### GET `/cgi-bin/api-preview_cdr`

Returns CDR preview/download.

**Query params:** `session_token`, `_nocache_`

---

## SIP Log

### GET `/cgi-bin/api-get_sip`

Returns SIP log existence check.

**Query params:** `session_token`, `_nocache_`

**Response:**
```json
{"results": [{"exist": "false"}]}
```

---

## Page-by-Page Field Reference

Below is every page visited in the capture, the P-parameters it requests, and the observed values. Display names are from the device locale data (`p_display_names.txt` and `locale_en.txt`).

---

### Status > System Info (`/status/systemInfo`)

**Request (frame 25):**
```
P89, serial_number, P917, tmp_fact_cfg_ver_str, P68, P69, P70, P45,
cpe_version, P199, cpu_load, system_status
```

**Response:**
| Field                  | Value                   | Display Name              |
|------------------------|-------------------------|---------------------------|
| `P89`                  | `HT802V2`              | Status                    |
| `serial_number`        | `XXXXXXXXXX`           | Serial Number             |
| `P917`                 | `V1.0A`                | Hardware Version          |
| `tmp_fact_cfg_ver_str` | `9610009410A`          | Factory Config Version    |
| `P68`                  | `1.0.9.3`              | Program                   |
| `P69`                  | `1.0.9.2`              | Boot                      |
| `P70`                  | `1.0.9.1`              | Core                      |
| `P45`                  | `1.0.9.3`              | Base                      |
| `cpe_version`          | `""`                   | CPE Version               |
| `P199`                 | `21:06:47 up 22 days`  | System Up Time            |
| `cpu_load`             | `18%`                  | CPU Load                  |
| `system_status`        | `""`                   | System Status             |

**Also fetches MAC (frame 40):**

| Field | Value              | Display Name |
|-------|--------------------|--------------|
| `P67` | `00:11:22:33:44:55`| MAC Address  |

---

### Status > Network Status (`/status/netStatus`)

**Request (frame 92):**
```
mac_display, P121, ipv6_addr, vpn_ip, vpn_ip6, net_cable_status,
P211, P80, cert_gen, system_status
```

**Response:**
| Field              | Value                                              | Display Name              |
|--------------------|----------------------------------------------------|---------------------------|
| `mac_display`      | `00:11:22:33:44:55`                               | MAC Address               |
| `P121`             | `MANAGE -- 10.0.0.1    SERVICE -- 10.0.0.2`  | IPv4 Address              |
| `ipv6_addr`        | `""`                                               | IPv6 Address              |
| `vpn_ip`           | `""`                                               | VPN IPv4 Address          |
| `vpn_ip6`          | `""`                                               | VPN IPv6 Address          |
| `net_cable_status` | `Up 100Mbps Full`                                  | Network Cable Status      |
| `P211`             | `Disabled`                                         | PPPoE Link Up             |
| `P80`              | `Unknown NAT`                                      | NAT                       |
| `cert_gen`         | `ECDSA+SHA384`                                     | Certificate Type          |
| `system_status`    | `""`                                               | System Status             |

---

### Status > Port Status (`/status/portStatus`)

**Request (frame 115):**
```
P4901, P35, P4921, sip_port_0, P4902, P735, P4061, P4922,
P4903..P4909, P4062..P4068, P4923..P4929, sip_port_1..sip_port_8,
dnd_0, forward_0, busyForward_0, delayedForward_0,
sendCID_0..sendCID_7, CW_0..CW_7, srtp_0..srtp_7,
dnd_1, forward_1, busyForward_1, delayedForward_1
```

**Response (key fields):**
| Field              | Value          | Display Name                   |
|--------------------|----------------|--------------------------------|
| `P4901`            | `On Hook`      | Hook                           |
| `P35`              | `15551234567`  | SIP User ID                    |
| `P4921`            | `Registered`   | Registration                   |
| `sip_port_0`       | `5060`         | Port 1 SIP Port               |
| `P4902`            | `On Hook`      | Hook                           |
| `P735`             | `""`           | SIP User ID                    |
| `P4922`            | `Not Registered`| Registration                  |
| `dnd_0`            | `0`            | DND                            |
| `forward_0`        | `""`           | Forward                        |
| `busyForward_0`    | `""`           | Busy Forward                   |
| `delayedForward_0` | `""`           | Delayed Forward                |
| `sendCID_0`        | `1`            | Port 1 Send Caller ID         |
| `CW_0`             | `1`            | Port 1 Call Waiting            |
| `srtp_0`           | `0`            | Port 1 SRTP                   |

Port indices 0-7 map to FXS1 accounts (0), FXS2 accounts (1), and additional virtual accounts (2-7, unused on HT802).

---

### Network Settings > Ethernet > Basic (`/networkSetting/ethernet/basicSet`)

**Request (frame 148):**
```
P1415, P8, P146, P147, P148, P82, P83, P269, P9..P28,
P92..P95, P5026..P5037, P1419, P1426, P1420..P1425, P1423,
P7901, P7902, P7903
```

**Response:**
| P-param  | Value       | Display Name                         | Type | Options/Range | Tooltip |
|----------|-------------|--------------------------------------|------|------------|------------|
| `P1415`  | `2`         | Ethernet Settings                    | enum | 2=IPv4 Only, 3=IPv6 Only, 0=Both, prefer IPv4, 1=Both, prefer IPv6 | Internet Protocol |
| `P8`     | `0`         | IPv4 Address Type (0=DHCP, 1=Static, 2=PPPoE) | enum | 0=Auto-configured, 2=Use PPPoE, 1=Statically configured | Configures how the IPv4 address is obtained on the device. |
| `P146`   | `""`        | Host Name (Option 12)                | string |  | Specifies the name of the client. This field is optional but may be required by Internet Service Providers. |
| `P147`   | `""`        | DHCP Domain                          | string |  | Specifies the DHCP Domain. This value is optional, but may be required by Internet Service Providers. |
| `P148`   | `HT8XXV2`   | Vendor Class ID (Option 60)          | string |  | Set the manufacturer identification number exchanged between the client and the server |
| `P82`    | `""`        | PPPoE Account ID                     | string |  | Enter the PPPoE account ID |
| `P83`    | `""`        | PPPoE Password                       | string (password) |  | Enter the PPPoE password |
| `P269`   | `""`        | PPPoE Service Name                   | string |  | Enter the PPPoE service name |
| `P9`     | `192`       | Static IP - Octet 1                  | int |  |  |
| `P10`    | `168`       | Static IP - Octet 2                  | int |  |  |
| `P11`    | `0`         | Static IP - Octet 3                  | int |  |  |
| `P12`    | `160`       | Static IP - Octet 4                  | int |  |  |
| `P13`    | `255`       | Subnet Mask - Octet 1               | int |  |  |
| `P14`    | `255`       | Subnet Mask - Octet 2               | int |  |  |
| `P15`    | `0`         | Subnet Mask - Octet 3               | int |  |  |
| `P16`    | `0`         | Subnet Mask - Octet 4               | int |  |  |
| `P17`    | `0`         | Gateway - Octet 1                   | int |  |  |
| `P18`    | `0`         | Gateway - Octet 2                   | int |  |  |
| `P19`    | `0`         | Gateway - Octet 3                   | int |  |  |
| `P20`    | `0`         | Gateway - Octet 4                   | int |  |  |
| `P21`..`P28` | `0`    | (Legacy IP octets / alternate)       | int |  |  |
| `P92`    | `0`         | Layer 2 QoS 802.1Q/VLAN Tag (Byte 1)| int |  |  |
| `P93`    | `0`         | Layer 2 QoS 802.1Q/VLAN Tag (Byte 2)| int |  |  |
| `P94`    | `0`         | Layer 2 QoS SIP 802.1p (Byte 1)     | int |  |  |
| `P95`    | `0`         | Layer 2 QoS SIP 802.1p (Byte 2)     | int |  |  |
| `P5026`..`P5037` | `0`| IPv6 Address Octets                  | int |  |  |
| `P1419`  | `0`         | IPv6 Address Type                    | enum | 0=Auto-configured, 1=Statically configured | Configures how the IPv6 address is obtained on the device. |
| `P1426`  | `0`         | Static address type                  | enum | 0=Full Static, 1=Prefix Static | Static address type |
| `P1420`  | `""`        | Static IPv6 Address                  | string |  |  |
| `P1421`  | `""`        | IPv6 Prefix Length                   | string |  |  |
| `P1422`  | `""`        | IPv6 Prefix (64 bits)               | string |  |  |
| `P1424`  | `""`        | DNS Server 1                         | string |  |  |
| `P1425`  | `""`        | DNS Server 2                         | string |  |  |
| `P1423`  | `""`        | Preferred DNS Server                 | string |  | Enter preferred DNS server address |
| `P7901`  | `0`         | 802.1X Mode                          | enum | 0=Disabled, 1=EAP_MD5, 2=EAP_TLS, 3=EAP-PEAPv0/MSCHAPv2 | Allow users to enable/disable 802.1X Mode |
| `P7902`  | `""`        | 802.1X Identity                      | string |  | Enter 802.1X identity information |
| `P7903`  | `""`        | 802.1X MD5 Password                  | string (password) |  | Enter 802.1X MD5 password |

---

### Network Settings > Advanced > Advanced Set (`/networkSetting/advanced/advancedSet`)

**Request (frame 163):**
```
P1684, P22122, P22119, P51, P5038, P5042, P1564, P8512, P475, P244, P28115
```

**Response:**
| P-param   | Value  | Display Name                          | Type | Options/Range | Tooltip |
|-----------|--------|---------------------------------------|------|------------|------------|
| `P1684`   | `1`    | Advanced Settings                     | boolean | 0=No, 1=Yes | Controls the LLDP (Link Layer Discovery Protocol) service. |
| `P22122`  | `60`   | LLDP TX Interval                      | int |  | Configures LLDP TX Interval (in seconds). Valid range is 1 to 3600. |
| `P22119`  | `1`    | Enable CDP                            | boolean | 0=No, 1=Yes | If enabled, the device will use the Cisco Discovery Protocol feature. |
| `P51`     | `2`    | Layer 2 QoS 802.1Q/VLAN Tag          | int |  | Used to identify and distinguish different VLANs, ranging from 0 to 4094. When configured to 0, the VLAN is invalid. |
| `P5038`   | `0`    | Layer 2 QoS SIP 802.1p               | int |  | 802.1p priority is the user priority defined in the TCI (Tag Control Information) field of the Layer 2 802.1Q tag header. When a switch is blocked, 802.1p priority can be used to determine which pa... |
| `P5042`   | `0`    | Layer 2 QoS RTP 802.1p               | int |  | 802.1p priority is the user priority defined in the TCI (Tag Control Information) field of the Layer 2 802.1Q tag header. When a switch is blocked, 802.1p priority can be used to determine which pa... |
| `P1564`   | `0`    | Use DNS to detect network connectivity| boolean | 0=No, 1=Yes |  |
| `P8512`   | `1`    | Use ARP to detect network connectivity| boolean | 0=No, 1=Yes |  |
| `P475`    | `3`    | Layer 3 QoS (DSCP)                   | int |  |  |
| `P244`    | `1500` | Maximum Transmission Unit (MTU)       | int |  | Configures the MTU in bytes. ( Default 1500 bytes. Range 576-1500 bytes ) |
| `P28115`  | `""`   | Black List for WAN Side Port          | string |  | Ports on the blocklist will be disabled on the device |

---

### Network Settings > Advanced > DNS Cache (`/networkSetting/advanced/dnsCache`)

**Request (frame 172):**
```
P93000..P93345 (series with stride 20, suffixes 00,01,02,03,05,07)
```

This is a table of up to 18 DNS cache/override entries. Each entry `i` (0-based, stride=20) has:

| Suffix | Display Name     | Example P-param |
|--------|------------------|-----------------|
| `00`   | Domain Name      | `P93000`        |
| `01`   | TTL              | `P93001`        |
| `02`   | Type             | `P93002`        |
| `03`   | Priority         | `P93003`        |
| `05`   | NAPTR Service    | `P93005`        |
| `07`   | Value            | `P93007`        |

Observed: all entries empty domain, TTL=300, type=0, priority=0, service=`SIP+D2U`, value=`""`.

---

### Network Settings > DDNS (`/networkSetting/DDNS`)

**Request:**
```
P28121, P28122, P28123, P28124, P28125, P28126
```

**Response:**
| P-param   | Value  | Display Name                          | Type | Options/Range | Tooltip |
|-----------|--------|---------------------------------------|------|------------|------------|
| `P28121`  | `0`    | DDNS Settings                         | boolean | 0=No, 1=Yes | Enable DDNS function |
| `P28122`  | `0`    | DDNS Server                           | enum | 0=dyndns.org, 1=freedns.afraid.org, 2=zoneedit.com, 3=no-ip.com, 4=oray.net, ... | Select DDNS server |
| `P28123`  | `""`   | DDNS Username                         | string |  | Set the username of the DDNS server |
| `P28124`  | `""`   | DDNS Password                         | string (password) |  | Set the password of the DDNS server |
| `P28125`  | `""`   | DDNS Hostname                         | string |  | Set the domain name of the DDNS server |
| `P28126`  | `""`   | DDNS Hash                             | string |  | Set the hash value of the DDNS server |

---

### Network Settings > OpenVPN (`/networkSetting/openVpn`)

**Request:**
```
P7050, P7051, P7052, P22597, P22598, P22599, P20714, P2912, P20716,
P20717, P20725, P8394, P8395, P20715, P22457, P8460
```

**Response:**
| P-param   | Value    | Display Name                          | Type | Options/Range | Tooltip |
|-----------|----------|---------------------------------------|------|------------|------------|
| `P7050`   | `0`      | OpenVPN Settings                      | boolean | 0=No, 1=Yes | Enable/Disable the OpenVPN® feature. |
| `P7051`   | `""`     | OpenVPN Server Address                | string |  | Address of OpenVPN® server |
| `P7052`   | `1194`   | OpenVPN Port                          | int |  | Port of OpenVPN® server |
| `P22597`  | `""`     | OpenVPN Server Secondary Address      | string |  | Configure OpenVPN® server secondary address. |
| `P22598`  | `1194`   | OpenVPN Secondary Port                | int |  | Configure OpenVPN® Secondary Port. |
| `P22599`  | `0`      | Randomly Select Server                | boolean | 0=No, 1=Yes | If enabled, a server will be randomly selected in the configuration to start OpenVPN requests. If closed, requests will be made in the order of server configuration. |
| `P20714`  | `tun`    | OpenVPN Interface type                | enum | tap=TAP, tun=TUN | Bridge (TAP) or routing (TUN) |
| `P2912`   | `udp`    | OpenVPN Transport                     | enum | udp=UDP, tcp=TCP | Configures network protocol used for OpenVPN®. |
| `P20716`  | `1`      | Enable OpenVPN LZO Compression        | boolean | 0=No, 1=Yes | Enable LZO compression algorithm on the VPN link. Please enable this compression algorithm after confirming that the LZO compression algorithm is enabled on the server |
| `P20717`  | `BF-CBC` | OpenVPN Encryption                    | string |  | Set OpenVPN® encryption algorithm |
| `P20725`  | `SHA1`   | OpenVPN Digest                        | string |  | Set OpenVPN® digest algorithm |
| `P8394`   | `""`     | OpenVPN Username                      | string |  | Configures OpenVPN® authentication username (optional). |
| `P8395`   | `""`     | OpenVPN Password                      | string (password) |  | Configures OpenVPN® authentication password (optional). |
| `P20715`  | `""`     | OpenVPN Client Key Password           | string (password) |  | Password for client.key file. |
| `P22457`  | `0`      | OpenVPN TLS Key Type                  | int |  | Select the encryption type of the OpenVPN® TLS key. |
| `P8460`   | `""`     | OpenVPN Additional Options            | string |  | Additional options to be appended to the OpenVPN® config file. Note: Additional options are separated by semicolon.<br>For example:connect-retry 5;tls-client;keepalive 10 60.Please use with caution... |

---

### System Settings > Basic (`/systemSetting/basic`)

**Request (frame 196):**
```
P253, P277, P28127, P88, P28181, P8457, P76, P84, P474
```

**Response:**
| P-param   | Value                    | Display Name                           | Type | Options/Range | Tooltip |
|-----------|--------------------------|----------------------------------------|------|------------|------------|
| `P253`    | `0`                      | Basic Settings                         | boolean | 0=No, 1=Yes |  |
| `P277`    | `0`                      | Enable Direct IP Call                  | boolean | 0=No, 1=Yes |  |
| `P28127`  | `""`                     | Blocklist For Incoming Calls           | string |  | Block calls from specific numbers. Use , to separate numbers |
| `P88`     | `0`                      | Lock Keypad Update                     | boolean | 0=No, 1=Yes | configuration update via keypad is disabled if set to Yes |
| `P28181`  | `0`                      | Play Busy Tone When Account is unregistered | boolean | 0=No, 1=Yes | If set to Yes, busy tone will be played when user goes offhook from an unregistered account. |
| `P8457`   | `3561`                   | DHCP Option 17 Enterprise Number       | int |  | Fill in the DHCP Option 17 enterprise number, the default is 3561 |
| `P76`     | `stun.grandstream.com`   | STUN Server                            | string |  | The IP address or domain name of the STUN server. Only non-symmetric NAT routers work with STUN. |
| `P84`     | `20`                     | Keep-Alive Interval                    | int |  |  |
| `P474`    | `0`                      | Use STUN to detect network connectivity| boolean | 0=No, 1=Yes | Use STUN keep-alive to detect WAN side network problems |

---

### System Settings > Timezone & Language (`/systemSetting/timezoneAndLang`)

**Request (frame 207):**
```
P30, P8333, P144, P64, P246, P143, P342
```

**Response:**
| P-param | Value                                              | Display Name                                        | Type | Options/Range | Tooltip |
|---------|----------------------------------------------------|-----------------------------------------------------|------|------------|------------|
| `P30`   | `pool.ntp.org`                                     | NTP Server                                          | string |  | Configures the URL or IP address of the NTP server. The device may obtain the date and time from the server. |
| `P8333` | `""`                                               | Secondary NTP Server                                | string |  | Configures the URL or IP address of the NTP server. The device may obtain the date and time from the server. |
| `P144`  | `1`                                                | Allow DHCP Option 42 to Override NTP Server         | boolean | 0=No, 1=Yes | When enabled, DHCP Option 42 will override the NTP server if it is set up on the LAN. |
| `P64`   | `CET-1CEST-2,M3.5.0/02:00:00,M10.5.0/03:00:00`   | Time Zone                                           | string |  | Configures the date/time used on the device according to the specified time zone. |
| `P246`  | `MTZ+6MDT+5,M3.2.0,M11.1.0`                       | Self-Defined Time Zone                              | string |  | This parameter allows the users to specify their own time zone. For syntax and examples, please refer to the user manual. |
| `P143`  | `1`                                                | Allow DHCP Option 2 to Override Time Zone Setting   | boolean | 0=No, 1=Yes | Allows device to get provisioned for Time Zone from DHCP Option 2 in the local server. |
| `P342`  | `0`                                                | IVR Language                                        | enum | 0=English, 4=Chinese, 6=Russian, 10=Spanish | Select IVR voice prompt language type |

---

### System Settings > Tone (`/systemSetting/tone`)

**Request:**
```
P4040, P4042, P4000, P4001, P4002, P4003, P4004, P4005, P4041, P28133, P28196, P28211
```

**Response:**
| P-param   | Value                                              | Display Name                    | Type | Options/Range | Tooltip |
|-----------|----------------------------------------------------|---------------------------------|------|------------|------------|
| `P4040`   | `c=2000/4000;`                                     | Ringtone                        | string |  | Cadence on+off value range (0, 16000) milliseconds |
| `P4042`   | `""`                                               | Prompt Tone Access Code         | string |  | Key pattern to get Prompt Tone. Maximum 20 digits. No default. |
| `P4000`   | `f1=350@-17,f2=440@-17,c=0/0;`                    | Dial Tone                       | string |  |  |
| `P4001`   | `f1=440@-17,f2=480@-17,c=2000/4000;`              | Ringback Tone                   | string |  |  |
| `P4002`   | `f1=480@-21,f2=620@-21,c=500/500;`                | Busy Tone                       | string |  |  |
| `P4003`   | `f1=480@-21,f2=620@-21,c=250/250;`                | Reorder Tone                    | string |  |  |
| `P4004`   | `f1=350@-11,f2=440@-11,c=100/100-100/100-100/100;`| Confirmation Tone               | string |  |  |
| `P4005`   | `f1=440@-13,c=300/10000;`                          | Call Waiting Tone               | string |  |  |
| `P4041`   | `f1=350@-17,f2=440@-17,c=0/0;`                    | Wait for Dial-Tone              | string |  |  |
| `P28133`  | `f1=425@-15,c=600/600;`                            | Conference Party Hangup Tone    | string |  |  |
| `P28196`  | `f1=350@-13, f2=440@-13, c=750/750-0/0;`          | Special Proceed Indication Tone | string |  |  |
| `P28211`  | `f1=350@-13, f2=450@-13, c=750/750;`              | Special Condition Tone          | string |  |  |

---

### System Settings > Security > Remote Access (`/systemSetting/security/remote`)

**Request (frame 215):**
```
P1650, P901, P27010, P28116, P28117, P1683, P28158, P28159,
P276, P27006, P28163, P28120, P28128, P28164, P28210, P20701, P20702
```

**Response:**
| P-param   | Value  | Display Name                              | Type | Options/Range | Tooltip |
|-----------|--------|-------------------------------------------|------|------------|------------|
| `P1650`   | `1`    | Web Access Mode                           | enum | 0=HTTPS, 1=HTTP, 2=Disabled | Sets the protocol for the web interface. |
| `P901`    | `80`   | HTTP Web Port                             | int |  | default is 80 |
| `P27010`  | `443`  | HTTPS Web Port                            | int |  | default is 443 |
| `P28116`  | `10`   | Web Session Timeout                       | int |  | Configures the timer to log out of the web session when idle. Default is 10 minutes. Range is 1-60 minutes. |
| `P28117`  | `5`    | Web Access Attempt Limit                  | int |  | Configures the number of failed web access attempts allowed before lockout. Default is 5. Range is 1-10. |
| `P1683`   | `15`   | Web Lockout Duration                      | int |  | Specifies the time in minutes that the web login interface will be locked out to user after number of login failures reach “Web Access Attempt Limits”. This lockout time is used for web login. Defa... |
| `P28158`  | `1`    | Enable User Level Web Access              | boolean | 0=No, 1=Yes |  |
| `P28159`  | `1`    | Enable Viewer Level Web Access            | boolean | 0=No, 1=Yes |  |
| `P276`    | `0`    | Enable SSH                                | boolean | 0=No, 1=Yes |  |
| `P27006`  | `22`   | SSH Port                                  | int |  | Configures the port for SSH access. Default is 22. Cannot be the same as the Telnet Port |
| `P28163`  | `0`    | SSH Idle Timeout                          | int |  | 0-86400 seconds. default 0 means never timeout. |
| `P28120`  | `1`    | Enable Telnet                             | boolean | 0=No, 1=Yes |  |
| `P28128`  | `23`   | Telnet Port                               | int |  | default is 23. Cannot be the same as SSH Port. |
| `P28164`  | `0`    | Telnet Idle Timeout                       | int |  | 0-86400 seconds. default 0 means never timeout. |
| `P28210`  | `3`    | Security Controls for SSH/Telnet Access   | enum | 0=Only allow SSH private IP users to set system Pvalue, 1=Allow all SSH users... | Specify security measures and controls that apply to the SSH/Telnet protocol to ensure secure and authorized access to the device |
| `P20701`  | `""`   | Allow List for WAN Side                   | string |  | If WAN-side Web/SSH access is set to Yes. Users can configure WAN side allowlist for remote management. Supports multiple IPs, which need to be separated by spaces; for example: 192.168.5.222 192.1... |
| `P20702`  | `""`   | Block List for WAN Side                   | string |  | If WAN-side Web/SSH access is set to Yes. Users can configure WAN side blocklist for remote management. Supports multiple IPs, which need to be separated by spaces; for example: 192.168.5.222 192.1... |

**Also loads port conflict check (frame 220):**
```
P901, P4518, P21903, P27010, P27006, P28128, P150..P157
```
(Used to validate port uniqueness)

---

### System Settings > Security > User Info (`/systemSetting/security/userInfo`)

**Request (frame 232):**
```
P28788, P28790, P28791, P28792
```

**Response:**
| P-param   | Value | Display Name                       | Type | Options/Range | Tooltip |
|-----------|-------|------------------------------------|------|------------|------------|
| `P28788`  | `1`   | Enable strict password rules       | boolean | 0=No, 1=Yes | Enable strict password rules. Non admin users cannot edit |
| `P28790`  | `8`   | Minimum password length            | int |  | Range: 4-30, default is 8. Non admin users cannot edit |
| `P28791`  | `3`   | Required number of character classes| int |  | Set the minimum number of character classes that a password should contain, composed of allowed combinations of different character classes;Range: 0-4, default is 3. Non admin users cannot edit |
| `P28792`  | `7`   | Allowed Character classes          | bitmask | 1=Lower case, 2=Upper case, 4=Numbers, 8=Special Characters |  |

---

### System Settings > Security > Certificate (`/systemSetting/security/certificate`)

**Request (frame 247):**
```
P8536, P22293, P22294
```

**Response:**
| P-param   | Value | Display Name                         | Type | Options/Range | Tooltip |
|-----------|-------|--------------------------------------|------|------------|------------|
| `P8536`   | `0`   | Enable/Disable Weak Cipher Suites    | enum | 0=Enable Weak TLS Ciphers Suites, 1=Disable Symmetric Encryption RC4/DES/3DES... |  |
| `P22293`  | `99`  | Minimum TLS Version                  | enum | 99=Unlimited, 10=TLS, 11=TLS, 12=TLS, 13=TLS | Configures the minimum TLS version supported by the device. Minimum TLS version must be less than or equal to maximum TLS version. |
| `P22294`  | `99`  | Maximum TLS Version                  | enum | 99=Unlimited, 10=TLS, 11=TLS, 12=TLS, 13=TLS | Configures the maximum TLS version supported by the device. Maximum TLS version must be greater than or equal to minimum TLS version. |

---

### System Settings > Security > CA Certificate (`/systemSetting/security/cacert`)

**Request (frame 255):**
```
P8502
```

**Response:**
| P-param | Value | Display Name                     | Type | Options/Range | Tooltip |
|---------|-------|----------------------------------|------|------------|------------|
| `P8502` | `0`   | Trusted CA Certificates          | enum | 0=Built-in trusted certificates, 1=Custom trusted certificates, 2=All trusted... | The device will verify the server certificate based on the built-in, custom or both trusted certificates list. |

---

### System Settings > Management > TR-069 (`/systemSetting/manageSet/tr069`)

**Request (frame 265):**
```
P1409, P4503, P4504, P4505, P4506, P4507, P4511, P4512, P4518, P8220, P8221
```

**Also loads port conflict check (frame 266).**

**Response:**
| P-param  | Value                              | Display Name                  | Type | Options/Range | Tooltip |
|----------|------------------------------------|-------------------------------|------|------------|------------|
| `P1409`  | `0`                                | Management Settings           | boolean | 0=No, 1=Yes | Configure whether to enable TR-069 |
| `P4503`  | `https://acsguestb.gdms.cloud`     | ACS URL                       | string |  | Configure the URL or IP address of the TR-069 automatic configuration server(ACS). For example: http: //acs.mycompany.com, or IP address. Note: The protocol header http or https must be included |
| `P4504`  | `""`                               | TR-069 Username               | string |  | Configure the user name used by ACS to authenticate the TR-069 client, that is, the device when the device initiates a connection request to ACS. This user name must be consistent with the configur... |
| `P4505`  | `""`                               | TR-069 Password               | string (password) |  | Configure the password used by ACS to authenticate the TR-069 client, that is, the device when the device initiates a connection request to ACS. This password must be consistent with the configurat... |
| `P4506`  | `0`                                | Periodic Inform Enable        | boolean | 0=No, 1=Yes |  |
| `P4507`  | `86400`                            | Periodic Inform Interval      | int |  | Configures periodic inform interval to send the inform packets to TR-069 Auto Configuration Server. |
| `P4511`  | `001122334455`                     | Connection Request Username   | string |  | The username for the TR-069 Auto Configuration Server to connect to the device. |
| `P4512`  | `""`                               | Connection Request Password   | string (password) |  | The password for the TR-069 Auto Configuration Server to connect to the device. |
| `P4518`  | `7547`                             | Connection Request Port       | int |  | The port for the TR-069 Auto Configuration Server to connect to the device. |
| `P8220`  | `""`                               | CPE SSL Certificate           | string |  | Configure the certificate file for the device to connect to the ACS over SSL |
| `P8221`  | `""`                               | CPE SSL Private Key           | string |  | Specify the certificate key for the device to connect to the ACS via SSL |

---

### System Settings > Management > SNMP (`/systemSetting/manageSet/snmp`)

**Request (frame 278):**
```
P21896, P21904, P21903, P21897, P21898, P21899, P21901, P21902,
P21900, P21905, P21910, P21906, P21907, P21911, P21916, P21912, P21913
```

**Also loads port conflict check (frame 283).**

**Response:**
| P-param   | Value | Display Name                      | Type | Options/Range | Tooltip |
|-----------|-------|-----------------------------------|------|------------|------------|
| `P21896`  | `0`   | SNMP Settings                     | boolean | 0=No, 1=Yes | Configures whether to enable/disable the SNMP feature. |
| `P21904`  | `3`   | SNMP Version                      | enum | 1=Version 1, 2=Version 2c, 3=Version 3 | Specifies the SNMP version |
| `P21903`  | `161` | SNMP Port                         | int |  | Specifies the SNMP Port. Default is 161. Range is 161 or 1025-65535. |
| `P21897`  | `""`  | SNMP Trap IP Address              | string |  | IP address of the SNMP trap receiver |
| `P21898`  | `162` | SNMP Trap Port                    | int |  | Specifies the port of the SNMP trap receiver. Default is 162. Range is 162 or 1025-65535. |
| `P21899`  | `2`   | SNMP Trap Version                 | enum | 1=Version 1, 2=Version 2c, 3=Version 3 | Trap version of the SNMP trap receiver |
| `P21901`  | `5`   | SNMP Trap Interval                | int |  | Configures the interval between each trap sent to the trap receiver. Default is 5 minutes. Range is 1-1440 minutes. |
| `P21902`  | `""`  | SNMPv1/v2c Community              | string |  | Enter SNMP community for SNMP authentication |
| `P21900`  | `""`  | SNMPv1/v2c Trap Community         | string |  | Community string associated to the trap. It must match the community string of the trap receiver. |
| `P21905`  | `""`  | SNMPv3 User Name                  | string |  | SNMPv3 username |
| `P21910`  | `0`   | SNMPv3 Security Level             | enum | 0=NoAuthUser, 1=AuthUser, 2=PrivUser | SNMPv3 security level |
| `P21906`  | `0`   | SNMPv3 Authentication Protocol    | enum | 0=None, 1=MD5, 2=SHA | SNMPv3 authentication protocol |
| `P21907`  | `0`   | SNMPv3 Privacy Protocol           | enum | 0=None, 1=DES, 2=AES|AES128 | SNMPv3 encryption protocol |
| `P21911`  | `""`  | SNMPv3 Trap User Name             | string |  | SNMPv3 Trap username |
| `P21916`  | `0`   | SNMPv3 Trap Security Level        | enum | 0=NoAuthUser, 1=AuthUser, 2=PrivUser | SNMPv3 Trap security level |
| `P21912`  | `0`   | SNMPv3 Trap Authentication Protocol | enum | 0=None, 1=MD5, 2=SHA | SNMPv3 Trap Authentication Protocol |
| `P21913`  | `0`   | SNMPv3 Trap Privacy Protocol      | enum | 0=None, 1=DES, 2=AES|AES128 | SNMPv3 Trap encryption protocol |

---

### System Settings > Management > Interface Management (`/systemSetting/manageSet/interfaceManage`)

**Request (frame 297):**
```
P28161, P28162, P28209, P8607, P8610, P28793,
P22111, P22112, P22105, P22106, P22107, P22108, P22109, P22110
```

**Response:**
| P-param   | Value             | Display Name                             | Type | Options/Range | Tooltip |
|-----------|-------------------|------------------------------------------|------|------------|------------|
| `P28161`  | `1`               | Management Interface                     | boolean | 0=No, 1=Yes | A network interface that serves the HTTP/HTTPS/SSH/TELNET protocol. If the management vlan is configured and is different from the service vlan, the management network port will be a vlan network p... |
| `P28162`  | `1`               | Management Access                        | enum | 0=Management Interface Only, 1=Both Service and Management Interfaces | Specify which network port can be used for HTTP/HTTPS/SSH/TELNET protocol |
| `P28209`  | `1`               | Enable SNMP Through Management Interface | boolean | 0=No, 1=Yes | Configure routing so that SNMP functionality is accessible through management |
| `P8607`   | `0`               | Enable TR069 Through Management Interface| boolean | 0=No, 1=Yes | Allows dedicated activation of TR-069 protocol access through a dedicated management interface for remote device management and configuration. Disabled by default. |
| `P8610`   | `1`               | Enable Syslog Through Management Interface| boolean | 0=No, 1=Yes | Configure routing so that Syslog functionality is accessible through management |
| `P28793`  | `0`               | Enable Radius Through Management Interface| boolean | 0=No, 1=Yes | Configure routing so that Radius functionality is accessible through management |
| `P22111`  | `1`               | 802.1Q/VLAN Tag                          | int |  | Used to identify and distinguish different VLANs, ranging from 0 to 4094. When configured to 0, the VLAN is invalid. |
| `P22112`  | `0`               | 802.1p Priority Value                    | int |  | 802.1p priority is the user priority defined in the TCI (Tag Control Information) field of the Layer 2 802.1Q tag header. When a switch is blocked, 802.1p priority can be used to determine which pa... |
| `P22105`  | `0`               | IPv4 Address Type                        | enum | 0=Auto-configured, 1=Statically configured | Configure the address type of the management network port |
| `P22106`  | `192.168.100.100` | IP Address                               | string |  | Configure the IPv4 address of the management network port |
| `P22107`  | `255.255.255.0`   | Subnet Mask                              | string |  | Enter subnet mask |
| `P22108`  | `192.168.100.1`   | Default Router                           | string |  | Enter default gateway |
| `P22109`  | `0.0.0.0`         | DNS Server 1                             | string |  | Enter DNS Server 1 |
| `P22110`  | `0.0.0.0`         | DNS Server 2                             | string |  | Enter DNS Server 2 |

---

### System Settings > RADIUS (`/systemSetting/radius`)

**Request:**
```
P28107, P28114, P28930, P28803, P28108, P28109, P28110, P28111, P28112
```

**Response:**
| P-param   | Value  | Display Name                             | Type | Options/Range | Tooltip |
|-----------|--------|------------------------------------------|------|------------|------------|
| `P28107`  | `0`    | RADIUS Settings                          | boolean | 0=No, 1=Yes | Select whether to enable RADIUS web access control. Default is no |
| `P28114`  | `1`    | Action upon Radius Auth Server Error     | enum | 0=Reject Access, 1=Authenticate Locally |  |
| `P28930`  | `0`    | Enable Bypass Locked State               | boolean | 0=No, 1=Yes | Once enabled, RADIUS accounts can bypass the webUI locked state caused by local accounts. |
| `P28803`  | `0`    | RADIUS Auth Protocol                     | enum | 0=PAP, 1=CHAP, 2=MsCHAPv1, 3=MsCHAPv2 | Configure RADIUS authentication protocol |
| `P28108`  | `""`   | RADIUS Auth Server Address               | string |  | Configure RADIUS authentication server address |
| `P28109`  | `1812` | RADIUS Auth Server Port                  | int |  | Configure RADIUS authentication server port |
| `P28110`  | `""`   | RADIUS Shared Secret                     | string (password) |  | Configure RADIUS shared password |
| `P28111`  | `42397`| RADIUS VSA Vendor ID                     | int |  | Configure the RADIUS VSA provider ID to match the RADIUS server's configuration. The default value for Grandstream Networks Inc is 42397 |
| `P28112`  | `35`   | RADIUS VSA Access Level Attribute        | int |  | Configure the RADIUS VSA access level attributes to match the configuration of the RADIUS server. Incorrect settings will cause Radius authentication to fail. |

---

### System Settings > E911/HELD (`/systemSetting/e911held`)

**Request:**
```
P8565, P8597, P8598, P8599, P8725, P8566, P8567, P8574, P8575, P8576,
P8577, P8578, P8579, P8580, P8581, P8582, P8583, P8584, P8585, P8586,
P8587, P8588, P8589, P8590, P8591, P8592, P8593, P8594, P8595, P8596,
P8568, P8569, P8570, P8571, P8572, P8573
```

**Response:**
| P-param   | Value                            | Display Name                     | Type | Options/Range | Tooltip |
|-----------|----------------------------------|----------------------------------|------|------------|------------|
| `P8565`   | `0`                              | Enable E911                      | boolean | 0=No, 1=Yes | Enable Enhanced 911 call |
| `P8597`   | `911`                            | E911 Emergency Numbers           | int |  |  |
| `P8598`   | `0`                              | Geolocation-Routing Header       | boolean | 0=No, 1=Yes |  |
| `P8599`   | `0`                              | Priority Header                  | boolean | 0=No, 1=Yes |  |
| `P8725`   | `0`                              | (E911 setting)                   | int |  |  |
| `P8566`   | `0`                              | HELD Protocol                    | int |  |  |
| `P8567`   | `0`                              | HELD Synchronization Interval    | int |  | The valid synchronization interval is between 30 to 1440 minutes. The synchronization is off when the interval is 0. |
| `P8574`   | `geodetic,civic,locationURI`     | HELD Location Types              | string |  |  |
| `P8575`   | `0`                              | HELD Use LLDP Information        | boolean | 0=No, 1=Yes |  |
| `P8576`   | `0`                              | HELD NAI                         | boolean | 0=No, 1=Yes | If 'Yes' is selected, the Network Access Identifier (NAI) is included as the device identity in location requests sent to the Location Information Server (LIS) |
| `P8577`   | `""`                             | PIDF-LO: Country (A1)           | string |  |  |
| `P8578`   | `""`                             | PIDF-LO: State/Province (A2)    | string |  |  |
| `P8579`   | `""`                             | PIDF-LO: City (A3)              | string |  |  |
| `P8580`   | `""`                             | PIDF-LO: Street (A4)            | string |  |  |
| `P8581`   | `""`                             | PIDF-LO: House Number (HNO)     | string |  |  |
| `P8582`   | `""`                             | PIDF-LO: House Number Suffix    | string |  |  |
| `P8583`   | `""`                             | PIDF-LO: Landmark (LMK)         | string |  |  |
| `P8584`   | `""`                             | PIDF-LO: Additional Location (LOC)| string |  |  |
| `P8585`   | `""`                             | PIDF-LO: Name (NAM)             | string |  |  |
| `P8586`   | `""`                             | PIDF-LO: Postal Code (PC)       | string |  |  |
| `P8587`   | `""`                             | PIDF-LO: Building (BLD)         | string |  |  |
| `P8588`   | `""`                             | PIDF-LO: Unit (UNIT)            | string |  |  |
| `P8589`   | `""`                             | PIDF-LO: Floor (FLR)            | string |  |  |
| `P8590`   | `""`                             | PIDF-LO: Room (ROOM)            | string |  |  |
| `P8591`   | `""`                             | PIDF-LO: Seat (SEAT)            | string |  |  |
| `P8592`   | `""`                             | PIDF-LO: Primary Road (PRD)     | string |  |  |
| `P8593`   | `""`                             | PIDF-LO: Road Section (RD)      | string |  |  |
| `P8594`   | `""`                             | PIDF-LO: Branch Road (BRD)      | string |  |  |
| `P8595`   | `""`                             | PIDF-LO: Sub-Branch Road (RDBR) | string |  |  |
| `P8596`   | `""`                             | PIDF-LO: Additional Code (ADDCODE)| string |  |  |
| `P8568`   | `""`                             | Location Server                  | string |  | Configure the primary Location Information Server (LIS) address |
| `P8569`   | `""`                             | Location Server Username         | string |  | Configure the user name of the primary Location Information Server (LIS) |
| `P8570`   | `""`                             | Location Server Password         | string (password) |  | Configure the password of the primary Location Information Server (LIS) |
| `P8571`   | `""`                             | Secondary Location Server        | string |  | Configure the secondary Location Information Server (LIS) address |
| `P8572`   | `""`                             | Secondary Location Server Username| string |  | Configure the user name of the secondary Location Information Server (LIS) |
| `P8573`   | `""`                             | Secondary Location Server Password| string (password) |  | Configure the password of the secondary Location Information Server (LIS) |

---

### Port Settings > Port 1 > General (`/portSetting/1/general`)

**Request (frame 323):**
```
P271, P47, P967, P4567, P48, P2333, P28096, P8617, P1411, P35, P36,
P3, P63, P5046, P5050, P103, P26040, P60056, P60055, P29095,
P2308, P2309, P2310, P52, P101, P197
```

**Response:**
| P-param   | Value                | Display Name                      | Type | Options/Range | Tooltip |
|-----------|----------------------|-----------------------------------|------|------------|------------|
| `P271`    | `1`                  | Account Active                    | int |  | Indicates whether the account is active. |
| `P47`     | `192.168.1.100`      | Primary SIP Server                | string |  | The URL or IP address, and port of the SIP server. This is provided by your VoIP service provider (e.g., sip.mycompany.com, or IP address) |
| `P967`    | `""`                 | Failover SIP Server               | string |  | Optional, used when primary server no response |
| `P4567`   | `0`                  | Prefer Primary SIP Server         | enum | 0=No, 1=Will register to Primary Server if Failover registration expires, 2=W... |  |
| `P48`     | `""`                 | Outbound Proxy                    | string |  | IP address or Domain name of the Primary Outbound Proxy, Media Gateway, or Session Border Controller. |
| `P2333`   | `""`                 | Backup Outbound Proxy             | string |  | Defines secondary outbound proxy that will be used when the primary proxy cannot be connected. |
| `P28096`  | `0`                  | Prefer Primary Outbound Proxy     | boolean | 0=No, 1=Yes | If set to yes, after expiration of registration, priority will be given to re-register with the primary proxy server. |
| `P8617`   | `sip.netcologne.de`  | From Domain                       | string |  | Optional, actual domain name, will override the from header |
| `P1411`   | `0`                  | Allow DHCP Option 120 to Override SIP Server | boolean | 0=No, 1=Yes | When enabled, the value of option 120 sent by the DHCP server will be used as the SIP server by the device. |
| `P35`     | `15551234567`        | SIP User ID                       | int |  | User account information, provided by your VoIP service provider. |
| `P36`     | `15551234567`        | SIP Authenticate ID               | int |  | SIP service subscriber's Authenticate ID used for authentication. It can be identical to or different from the SIP User ID. |
| `P3`      | `015551234567`       | Name                              | int |  | The SIP server subscriber's name (optional) that will be used for Caller ID display (e.g., John Doe). |
| `P63`     | `1`                  | Tel URI                           | enum | 0=Disabled, 1=User=Phone, 2=Enabled |  |
| `P5046`   | `26`                 | Layer 3 QoS SIP DSCP             | int |  | Diff-Serv value in decimal, 0-63, default 26 |
| `P5050`   | `46`                 | Layer 3 QoS RTP DSCP             | int |  | Diff-Serv value in decimal, 0-63, default 46 |
| `P103`    | `0`                  | DNS Mode                          | enum | 0=A, 1=SRV, 2=NAPTR/SRV, 3=Use Configured IP |  |
| `P26040`  | `0`                  | DNS SRV Failover Mode             | enum | 0=Default, 1=Use current server until DNS TTL, 2=Use current server until no ... |  |
| `P60056`  | `60`                 | Failback Timer                    | int |  | Specifies the duration (in minutes) since failover to the current SIP server or Outbound Proxy before making failback attempts to the primary SIP server or Outbound Proxy. Default is 60 minutes, wi... |
| `P60055`  | `2`                  | Maximum Number of SIP Request Retries | int |  | Sets the maximum number of retries for the device to send requests to the server. If the destination address does not respond, all request messages are resent to the same address according to the c... |
| `P29095`  | `0`                  | Register Before DNS SRV Failover  | boolean | 0=No, 1=Yes | Configures whether to send REGISTER requests to the failover SIP server or outbound proxy before sending INVITE requests in the event of a DNS SRV failover. |
| `P2308`   | `""`                 | Primary IP                        | string |  |  |
| `P2309`   | `""`                 | Backup IP 1                       | string |  |  |
| `P2310`   | `""`                 | Backup IP 2                       | string |  |  |
| `P52`     | `0`                  | NAT Traversal                     | enum | 0=No, 2=Keep-Alive, 1=STUN, 3=UPnP, 4=Auto, 5=VPN | Configures whether NAT traversal mechanism is activated. Please refer to user manual for more details. |
| `P101`    | `""`                 | Use NAT IP                        | string |  | Configures the NAT IP address used in SIP/SDP messages. It should ONLY be used if required by your ITSP. |
| `P197`    | `""`                 | Proxy-Require                     | string |  | Fill in the SIP proxy. This configuration is used to notify the SIP server that the device is behind NAT or a firewall. If you configure this, please ensure that the SIP server you are using suppor... |

---

### Port Settings > Port 1 > SIP (`/portSetting/1/sip`)

**Request (frame 331):**
```
P31, P130, P81, P109, P32, P2330, P138, P60096, P60097, P60098,
P26002, P28756, P28784, P2397, P2398, P2399, P99, P60068, P40,
P20501, P26003, P135, P4562, P288, P60081, P60080, P2329, P2331,
P4891, P2338, P2339, P26058, P26059, P29098, P4437, P209, P250,
P60074, P2387, P60075, P137, P272, P2359, P60064, P29071, P4834,
P26061, P29090, P95023, P2395, P260, P261, P262, P263, P264, P266,
P267, P265, P28744
```

**Also loads SIP ports (frame 336):** `P40, P640, P740`

**Response (key fields):**
| P-param   | Value  | Display Name                                              | Type | Options/Range | Tooltip |
|-----------|--------|-----------------------------------------------------------|------|------------|------------|
| `P31`     | `1`    | SIP Registration                                          | boolean | 0=No, 1=Yes | Selects whether the device will send SIP REGISTER messages to the proxy/server. |
| `P130`    | `0`    | SIP Transport                                             | enum | 0=UDP, 1=TCP, 2=TLS | Set the network protocol used for SIP message transmission. |
| `P81`     | `0`    | Unregister On Reboot                                      | enum | 0=No, 1=All, 2=Instance |  |
| `P109`    | `1`    | Outgoing Call without Registration                        | boolean | 0=No, 1=Yes | Allow dialing without registering a SIP server |
| `P32`     | `60`   | Register Expiration                                       | int |  | Specifies the frequency (in minutes) in which the device refreshes its registration with the specified registrar. The maximum value is 64800 (about 45 days). |
| `P2330`   | `0`    | Re-Register before Expiration                             | int |  | Specifies the time frequency (in seconds) that the device sends re-registration request before the register expiration. Default is 0 second. Rang is 0-64800 (about 45 minutes). |
| `P138`    | `20`   | SIP Registration Failure Retry Wait Time                  | int |  | Specifies the interval (in seconds) to retry registration if the process failed. Default is 20 seconds. Valid range is 1 to 3600. |
| `P60096`  | `0`    | Use Random SIP Registration Failure Retry Wait Time       | int |  | When enabled, the waiting time to resend a registration request in case of SIP registration failure will become a random number in the following range. |
| `P60097`  | `60`   | (SIP Timer setting)                                       | int |  |  |
| `P60098`  | `600`  | (SIP Timer setting)                                       | int |  |  |
| `P26002`  | `1200` | SIP Registration Failure Retry Wait Time upon 403 Forbidden| int |  | In seconds. Between 0-3600, default is 1200. 0 means stop retry registration upon 403 response. |
| `P28756`  | `0`    | Port Voltage Off upon no SIP Registration or SIP Registration Failure | int |  | in minutes. Between 0-60, default is 0. 0 means port voltage is never turned off |
| `P28784`  | `0`    | Delay Time of Port Voltage Off Timer Since Boot           | int |  | in minutes. Between 0-60, default is 0 |
| `P2397`   | `0`    | Enable SIP OPTIONS/NOTIFY Keep Alive                      | enum | 0=No, 1=OPTIONS, 2=NOTIFY | Configures whether to enable SIP OPTIONS/NOTIFY to track account registration status. If enabled, the device will send periodic OPTIONS/NOTIFY messages to server to track the connection status with... |
| `P2398`   | `30`   | SIP OPTIONS/NOTIFY Keep Alive Interval                    | int |  | Configures the time interval (in seconds) the device sends OPTIONS/NOTIFY message to the server. Default is 30 seconds. Range is 1-64800 seconds. |
| `P2399`   | `3`    | SIP OPTIONS/NOTIFY Keep Alive Max Lost                    | int |  |  |
| `P99`     | `0`    | SUBSCRIBE for MWI                                         | boolean | 0=No, 1=Yes |  |
| `P60068`  | `0`    | Subscribe Retry Wait Time upon 403 Forbidden              | int |  |  |
| `P40`     | `5060` | Local SIP Port                                            | int |  | Configures the local SIP port used to listen and transmit. |
| `P20501`  | `0`    | Use Random SIP Port                                       | boolean | 0=No, 1=Yes | Use a random SIP port instead of the above set port |
| `P26003`  | `1`    | Hold Target Before Refer                                  | boolean | 0=No, 1=Yes | Select whether to send ReINVITE before sending REFER to keep the third party in call transfer |
| `P135`    | `0`    | Refer-To Use Target Contact                               | boolean | 0=No, 1=Yes |  |
| `P4562`   | `0`    | Remove OBP from Route Header                              | boolean | 0=No, 1=Yes | When set to 'Yes', the SIP extension on the gateway will notify the SIP server that it's behind a NAT/Firewall |
| `P288`    | `1`    | Support SIP Instance ID                                   | boolean | 0=No, 1=Yes | Configures whether SIP Instance ID is supported or not. |
| `P60081`  | `0`    | Support outbound                                          | boolean | 0=No, 1=Yes | Support outbound |
| `P60080`  | `0`    | Support GRUU                                              | boolean | 0=No, 1=Yes | Support GRUU |
| `P2329`   | `1`    | SIP URI Scheme When Using TLS                             | enum | 0=sip, 1=sips |  |
| `P2331`   | `0`    | Use Actual Ephemeral Port in Contact with TCP/TLS         | boolean | 0=No, 1=Yes | Configures whether the actual ephemeral port in Contact header will be used when TLS/TCP is selected for SIP Transport. |
| `P4891`   | `0`    | Use Routing ID in SIP INVITE Header                       | int |  | Use Routing ID in SIP INVITE Header |
| `P2338`   | `0`    | Use Privacy Header                                        | enum | 0=Default, 1=No, 2=Yes |  |
| `P2339`   | `0`    | Use P-Preferred-Identity Header                           | enum | 0=Default, 1=No, 2=Yes |  |
| `P26058`  | `1`    | Use P-Access-Network-Info Header                          | boolean | 0=No, 1=Yes | Controls whether the P-Access-Network-Info header will be present in the SIP INVITE messages. Please refer to the user manual for more details. |
| `P26059`  | `1`    | Use P-Emergency-Info Header                               | boolean | 0=No, 1=Yes | Controls whether the P-Emergency-Info header will be present in the SIP INVITE messages. Please refer to the user manual for more details. |
| `P29098`  | `0`    | Use P-Asserted-Identity Header                            | boolean | 0=No, 1=Yes | Controls whether the P-Asserted-Identity header will be present in the SIP INVITE messages. Please refer to the user manual for more details. |
| `P4437`   | `0`    | SIP REGISTER Contact Header Uses                          | enum | 0=LAN Address, 1=WAN Address | SIP REGISTER Contact Header Uses LAN address or WAN address |
| `P209`    | `50`   | SIP T1 Timeout                                            | enum | 50=0.5, 100=1, 200=2, 400=4, 800=8 | Set SIP T1 timeout, the default value is 0.5 seconds |
| `P250`    | `400`  | SIP T2 Timeout                                            | enum | 200=2, 400=4, 800=8, 1600=16, 3200=32 | Set SIP T2 timeout, the default value is 4 seconds |
| `P60074`  | `0`    | SIP Timer B                                               | int |  | 0-128 sec. Default 0, which means using 64*T1. |
| `P2387`   | `0`    | SIP Timer D                                               | int |  | 0 - 64 seconds. Default 0 |
| `P60075`  | `0`    | SIP Timer F                                               | int |  | 0-128 sec. Default 0, which means using 64*T1. |
| `P137`    | `0`    | Enable Multiple m line in SDP                             | boolean | 0=No, 1=Yes |  |
| `P272`    | `0`    | Enable 100rel                                             | boolean | 0=No, 1=Yes | When enabled, the 100rel tag is appended to the value of the Supported header field of the initial signaling messages. |
| `P2359`   | `0`    | Add Auth Header on Initial REGISTER                       | boolean | 0=No, 1=Yes | If enabled, the device will add Authorization header field in initial REGISTER request. |
| `P60064`  | `0`    | Enable Call Waiting Alert-Info in 180 Ringing Response    | boolean | 0=No, 1=Yes | Activate the call waiting feature by including a call waiting reminder message in the 180 ring response sent to the caller when the call comes in. The default value is No |
| `P29071`  | `""`   | SIP User-Agent                                            | string |  | When not configured, the default value will be used |
| `P4834`   | `""`   | SIP User-Agent Postfix                                    | string |  | Configure SIP User-Agent suffix |
| `P26061`  | `0`    | Add MAC in User-Agent                                     | enum | 0=No, 1=Yes except REGISTER, 2=Yes to all SIP |  |
| `P29090`  | `0`    | Use MAC Header                                            | enum | 0=No, 1=REGISTER Only, 2=Yes to all request SIP |  |
| `P95023`  | `0`    | CSeq Tracking Mode                                        | enum | 0=per-call, 1=per-dialog | Sets the CSeq tracking mode to per-call or per-dialog |
| `P2395`   | `1`    | Enable Session Timer                                      | boolean | 0=No, 1=Yes |  |
| `P260`    | `180`  | Session Expiration                                        | int |  | Session Expiration is the time (in seconds) where the session is considered timed out, provided no successful session refresh transaction occurs beforehand. Default is 180 seconds. Range is 90-64800. |
| `P261`    | `90`   | Min-SE                                                    | int |  | The minimum session expiration (in seconds). Default is 90 seconds. Range is 90-64800. |
| `P262`    | `0`    | Caller Request Timer                                      | boolean | 0=No, 1=Yes |  |
| `P263`    | `0`    | Callee Request Timer                                      | boolean | 0=No, 1=Yes |  |
| `P264`    | `0`    | Force Timer                                               | boolean | 0=No, 1=Yes |  |
| `P266`    | `0`    | UAC Specify Refresher                                     | enum | 1=UAC, 2=UAS, 0=Omit(Recommended) |  |
| `P267`    | `1`    | UAS Specify Refresher                                     | enum | 1=UAC, 2=UAS | As a callee, select UAC to use caller or proxy server as the refresher, or select UAS to use the device as the refresher. |
| `P265`    | `0`    | Force INVITE                                              | boolean | 0=No, 1=Yes |  |
| `P28744`  | `0`    | When To Restart Session After Re-INVITE received          | enum | 0=Immediately, 1=After replying 200OK |  |

SIP Ports response:
| P-param | Value  | Display Name                | Type | Options/Range | Tooltip |
|---------|--------|-----------------------------|------|------------|------------|
| `P40`   | `5060` | Port 1 Local SIP Port       | int |  | Configures the local SIP port used to listen and transmit. |
| `P640`  | `7060` | Port 1 Local SIP TLS Port   | int |  | Configures the local SIP port used to listen and transmit. |
| `P740`  | `5062` | Port 2 Local SIP Port       | int |  | Configures the local SIP port used to listen and transmit. |

---

### Port Settings > Port 1 > Codec (`/portSetting/1/codec`)

**Request (frame 344):**
```
P850, P851, P852, P28794, P28134, P28138, P79, P95007, P28772,
P28201, P28205, P28804, P28808, P28812, P28816, P4825, P28173, P28177,
P57, P58, P59, P60, P61, P62, P46, P98, P37, P49, P97, P20529,
P96, P2385, P26073, P26074, P26075, P50, P4363, P228, P28913,
P4416, P28923, P133, P132, P2363, P39, P20505, P60084, P60085,
P291, P2392, P28839, P183, P2383, P26093, P26094, P26095
```

**Response:**
| P-param   | Value  | Display Name                                         | Type | Options/Range | Tooltip |
|-----------|--------|------------------------------------------------------|------|------------|------------|
| `P850`    | `101`  | Codec Settings                                       | int |  |  |
| `P851`    | `102`  | (Preferred Codec Choice 2)                           | int |  |  |
| `P852`    | `100`  | (Preferred Codec Choice 3)                           | int |  |  |
| `P28794`  | `0`    | Force DTMF to be sent via SIP INFO simultaneously   | boolean | 0=No, 1=Yes | Force DTMF to be sent via SIP INFO simultaneously |
| `P28134`  | `100`  | Inband DTMF Duration                                 | int |  |  |
| `P28138`  | `50`   | (Inband DTMF Duration - profile 3)                   | int |  |  |
| `P79`     | `101`  | DTMF Payload Type                                    | int |  | Configures the payload type for DTMF using RFC2833. Cannot be the same as iLBC or Opus payload type. |
| `P95007`  | `0`    | Enable Multiple Sampling Rates in SDP telephone-event| int |  | Enable Multiple Sampling Rates in SDP telephone-event |
| `P28772`  | `6`    | Inband DTMF Tx Gain                                  | int |  | Range: -12-12 dB, default is 6 |
| `P28201`  | `30`   | DSP DTMF Detector Duration Threshold                 | int |  |  |
| `P28205`  | `30`   | (iLBC Frame Size)                                    | int |  |  |
| `P28804`  | `-25`  | DSP DTMF Detector Min Level                          | int |  | Range: -45-0 dBm, default is -25 |
| `P28808`  | `1`    | DSP DTMF Detector Snr                                | int |  | Range: 0-12, default is 1 |
| `P28812`  | `25`   | DSP DTMF Detector Deviation                          | int |  | Range: 0-25, default is 25 |
| `P28816`  | `5`    | DSP DTMF Detector Twist                              | int |  | Range: 0-12dB, default is 5 |
| `P4825`   | `0`    | Enable DTMF Negotiation                              | int |  | If negotiaton is disabled, the above DTMF order will be used. |
| `P28173`  | `8`    | RFC2833 Events Count                                 | int |  | between 2 and 10, default is 8, 0 means continuous RFC2833 events |
| `P28177`  | `3`    | RFC2833 End Events Count                             | int |  | Between 2 and 10, the default value is 3 |
| `P57`     | `9`    | Vocoder Settings (1st)                               | int |  |  |
| `P58`     | `8`    | (Vocoder 2nd)                                        | int |  |  |
| `P59`     | `0`    | (Vocoder 3rd)                                        | int |  |  |
| `P60`     | `18`   | (Vocoder 4th)                                        | int |  |  |
| `P61`     | `2`    | (Vocoder 5th)                                        | int |  |  |
| `P62`     | `97`   | (Vocoder 6th)                                        | int |  |  |
| `P46`     | `123`  | (DTMF Payload)                                       | int |  |  |
| `P98`     | `4`    | (Silence Suppression setting)                        | int |  |  |
| `P37`     | `2`    | Voice Frames per TX                                  | int |  |  |
| `P49`     | `0`    | G.723 Rate                                           | int |  | Selects encoding rate for G.723 codec. |
| `P97`     | `0`    | iLBC Frame Size                                      | int |  | Selects iLBC packet frame size. |
| `P20529`  | `0`    | Enable Opus Stereo in SDP                            | boolean | 0=No, 1=Yes |  |
| `P96`     | `97`   | iLBC Payload Type                                    | int |  | Specifies iLBC payload type. Valid range is 96 to 127. Cannot be the same as Opus or DTMF payload type. |
| `P2385`   | `123`  | Opus Payload Type                                    | int |  | Specifies Opus payload type. Valid range is 96 to 127. It cannot be the same as iLBC or DTMF Payload Type. |
| `P26073`  | `0`    | Enable Audio RED with FEC                            | boolean | 0=No, 1=Yes |  |
| `P26074`  | `121`  | Audio FEC Payload Type                               | int |  | Configures audio FEC payload type. The valid range is from 96 to 127. The default value is 121. |
| `P26075`  | `124`  | Audio RED Payload Type                               | int |  | Configures audio RED payload type. The valid range is from 96 to 127. The default value is 124. |
| `P50`     | `0`    | Silence Suppression                                  | boolean | 0=No, 1=Yes |  |
| `P4363`   | `0`    | Use First Matching Vocoder in 200OK SDP              | boolean | 0=No, 1=Yes | When enabled, the gateway will use the first matching code in 200OK SDP to make calls |
| `P228`    | `0`    | Fax Mode                                             | enum | 0=T.38, 1=Pass-Through | Fax Mode |
| `P28913`  | `2`    | T.38 Max Bit Rate                                    | enum | 1=4800bps, 2=9600bps, 3=14400bps | Selects the maximum T.38 bit rate.Lowering the maximum fax bit rate may help improve the fax success rate.<br/> Only effective when the fax machine is fax receipt. |
| `P4416`   | `1`    | Re-INVITE After Fax Tone Detected                    | boolean | 0=No, 1=Yes | Allow the device to issue a T.38 or fax pass re-invite if fax tones are detected. Enabled by default |
| `P28923`  | `0`    | Re-INVITE Upon CNG Count                             | int |  | 0: this feature is disabled; Equal to or greater than 1: ATA will initial Re-Invite request when CNG count is reached; The valid range is [0, 6]. |
| `P133`    | `1`    | Jitter Buffer Type                                   | enum | 0=Fixed, 1=Adaptive | Selects either Fixed or Adaptive based on network conditions. |
| `P132`    | `1`    | Jitter Buffer Length                                  | int |  | Selects Low, Medium, or High based on network conditions. |
| `P2363`   | `1`    | Crypto Life Time                                     | boolean | 0=No, 1=Yes | Configures whether to enable Crypto Life Time. |
| `P39`     | `5004` | Local RTP Port                                       | int |  | Configures the local RTP port used to listen and transmit. Valid range is 1024 to 65535 and it must be even. |
| `P20505`  | `0`    | Use Random RTP Port                                  | boolean | 0=No, 1=Yes | Use a random RTP port instead of the above set port |
| `P60084`  | `""`   | Random RTP Port Range                                |  |  |  |
| `P60085`  | `""`   | (Codec setting)                                      |  |  |  |
| `P291`    | `0`    | Symmetric RTP                                        | boolean | 0=No, 1=Yes |  |
| `P2392`   | `1`    | Enable RTCP                                          | boolean | 0=No, 1=Yes | Allow users to enable RTCP |
| `P28839`  | `0`    | RTP/RTCP Keep Alive On Hold                          | boolean | 0=No, 1=Yes | RTP/RTCP Keep Alive On Hold |
| `P183`    | `0`    | SRTP Mode                                            | int |  | Enables and selects SRTP mode. |
| `P2383`   | `0`    | SRTP Key Length                                      | int |  | The cipher method/key length to use if SRTP is enabled. |
| `P26093`  | `""`   | VQ RTCP-XR Collector Name                            |  |  | Configures the host name of the central report collector that accepts voice quality reports contained in SIP PUBLISH messages. |
| `P26094`  | `""`   | VQ RTCP-XR Collector Address                         |  |  | Configures the IP address of the central report collector that accepts voice quality reports contained in SIP PUBLISH messages. |
| `P26095`  | `5060` | VQ RTCP-XR Collector Port                            | int |  | Configures the port of the central report collector that accepts voice quality reports contained in SIP PUBLISH messages. |

---

### Port Settings > Port 1 > Analog Line (`/portSetting/1/analogline`)

**Request (frame 352):**
```
P854, P853, P4661, P4662, P205, P892, P21925, P856, P20521,
P28165, P4424, P251, P252, P833, P247, P249, P824, P4429, P4234, P28192
```

**Response:**
| P-param   | Value  | Display Name                                          | Type | Options/Range | Tooltip |
|-----------|--------|-------------------------------------------------------|------|------------|------------|
| `P854`    | `9`    | Analog Signal Line Configuration                      | int |  | Select the area for SLIC configuration |
| `P853`    | `1`    | Caller ID Scheme                                      | int |  | Select caller ID mechanism |
| `P4661`   | `0`    | DTMF Caller ID                                        | int |  |  |
| `P4662`   | `0`    | (Rx Mute)                                             | int |  |  |
| `P205`    | `1`    | Polarity Reversal                                     | boolean | 0=No, 1=Yes | Reverse polarity upon call establishment and termination |
| `P892`    | `1`    | Loop Current Disconnect                               | boolean | 0=No, 1=Yes | Loop current disconnect upon call termination |
| `P21925`  | `1`    | Play busy/reorder tone before Loop Current Disconnect | boolean | 0=No, 1=Yes | Play busy/reorder tone before loop current disconnect upon call fail |
| `P856`    | `200`  | Loop Current Disconnect Duration                      | int |  | 100 - 10000 milliseconds. Default 200 milliseconds |
| `P20521`  | `0`    | Enable Pulse Dialing                                  | boolean | 0=No, 1=Yes | If set to No, there will be no function to detect pulse dialing |
| `P28165`  | `0`    | Pulse Dialing Standard                                | enum | 0=General Standard, 1=Swedish Standard, 2=New Zealand Standard | Pulse Dialing Standard |
| `P4424`   | `1`    | Enable Hook Flash                                     | boolean | 0=No, 1=Yes | Enable Hook Flash |
| `P251`    | `300`  | Hook Flash Timing                                     | int |  | In 40-2000 milliseconds range, Min - Max |
| `P252`    | `1100` | (On-hook timer)                                       | int |  |  |
| `P833`    | `400`  | On Hook Timing                                        | int |  | In 40-2000 milliseconds range, default is 400 |
| `P247`    | `0`    | Gain                                                  | int |  |  |
| `P249`    | `6`    | (Number setting)                                      | int |  |  |
| `P824`    | `0`    | Enable Line Echo Canceller (LEC)                      | boolean | 0=No, 1=Yes |  |
| `P4429`   | `20`   | Ring Frequency                                        | int |  | Selects ringing frequency settings |
| `P4234`   | `0`    | Ring Power                                            | int |  | Selects ringing power settings |
| `P28192`  | `2`    | OnHook DC Feed Current                                | int |  | Selects the DC feed current under on-hook |

---

### Port Settings > Port 1 > Call Settings (`/portSetting/1/call`)

**Request (frame 364):**
```
P71, P4045, P85, P29, P66, P4200, P72, P28147, P26062, P91,
P714, P186, P65, P129, P4420, P28760, P4793, P4360, P29072,
P855, P4371, P28197, P4560, P4820, P139, P74, P28080, P28169,
P185, P2324, P28153, P29073, P29096, P1406, P20525
```

**Response:**
| P-param   | Value  | Display Name                               | Type | Options/Range | Tooltip |
|-----------|--------|--------------------------------------------|------|------------|------------|
| `P71`     | (val)  | Off-hook Auto Dial                         |  |  | User ID/extension to dial automatically when offhook |
| `P4045`   | (val)  | Offhook Auto-Dial Delay                    | int |  | 0-60 seconds, default is 0 |
| `P85`     | `4`    | No Key Entry Timeout                       | int |  | Configures the timeout (in seconds) for no key entry. If no key is pressed after the timeout, the collected digits will be sent out. |
| `P29`     | (val)  | Early Dial                                 | boolean | 0=No, 1=Yes |  |
| `P66`     | (val)  | Dial Plan Prefix                           | string |  | Configures a prefix added to all numbers when making outbound calls. |
| `P4200`   | (val)  | Dial Plan                                  | string |  | Set gateway dialing rules. Please refer to the user manual for specific syntax and examples |
| `P72`     | `1`    | Use # as Dial Key                          | boolean | 0=No, 1=Yes |  |
| `P28147`  | (val)  | Enable # as Redial Key                     | int |  |  |
| `P26062`  | (val)  | RFC2543 Hold                               | int |  |  |
| `P91`     | (val)  | Enable Call-Waiting                        | boolean | 0=No, 1=Yes |  |
| `P714`    | `0`    | Enable Call-Waiting Caller ID              | boolean | 0=No, 1=Yes |  |
| `P186`    | `0`    | Enable Call-Waiting Tone                   | boolean | 0=No, 1=Yes | Enables Call Waiting alert tone when another incoming call is received while a call is in progress. |
| `P65`     | `0`    | Send Anonymous                             | boolean | 0=No, 1=Yes |  |
| `P129`    | `0`    | Anonymous Call Rejection                   | boolean | 0=No, 1=Yes |  |
| `P4420`   | (val)  | Outgoing Call Duration Limit               | int |  | 0-180 minutes, default is 0 (No Limit) |
| `P28760`  | (val)  | Incoming Call Duration Limit               | int |  | 0-180 minutes, default is 0 (No Limit) |
| `P4793`   | (val)  | Enable Receiver Offhook Tone               | boolean | 0=No, 1=Yes |  |
| `P4360`   | (val)  | Enable Reminder Ring for On-Hold Call      | boolean | 0=No, 1=Yes |  |
| `P29072`  | (val)  | Enable Reminder Ring for DND               | boolean | 0=No, 1=Yes |  |
| `P855`    | `0`    | Enable Visual MWI                          | boolean | 0=No, 1=Yes |  |
| `P4371`   | (val)  | Visual MWI Type                            | int |  | Configure the type of message waiting prompt (MWI) |
| `P28197`  | (val)  | MWI Tone                                   | enum | 0=Default, 1=Special Proceed Indication Tone | MWI Tone |
| `P4560`   | (val)  | Transfer on Conference Hangup              | boolean | 0=No, 1=Yes | When the conference initiator hangs up, whether to transfer the session so that other participants can continue the conference |
| `P4820`   | (val)  | Ringing Transfer                           | boolean | 0=No, 1=Yes | Defines whether the call is transferred to the other party When the transferring party hangs up while listening to the ringback tone. |
| `P139`    | `20`   | No Answer Timeout                          | int |  | Defines the timeout (in seconds) before the call is forwarded on no answer. Valid range is 1 to 120. |
| `P74`     | `0`    | Send Hook Flash Event                      | boolean | 0=No, 1=Yes | Hook Flash will be sent as a DTMF event if set to Yes |
| `P28080`  | (val)  | Flash Digit Control                        | boolean | 0=No, 1=Yes | Overrides the default settings for call control when both channels are in use |
| `P28169`  | (val)  | Callee Flash to 3WC                        | boolean | 0=No, 1=Yes | In call waiting scenarios, hookflash switches between two calls by default. After turning on the option, enter a three-party conference |
| `P185`    | `60`   | Ring Timeout                               | int |  | Set the no-answer timeout for incoming calls. The unit is seconds. Valid values range from 0 to 300. 0 means to turn off the function |
| `P2324`   | `0`    | Caller ID Display                          | enum | 0=Auto, 1=Disabled, 2=From Header |  |
| `P28153`  | (val)  | Enable Unknown Caller ID                   | int |  |  |
| `P29073`  | (val)  | Replace Beginning '+' with 00 in Caller ID| boolean | 0=No, 1=Yes | Replace Beginning '+' with 00 in Caller ID |
| `P29096`  | (val)  | Number of Beginning Digits to Strip from Caller ID | int |  | Range is between 0 and 10, default is 0 |
| `P1406`   | `0`    | Escape '#' as %23 in SIP URI               | boolean | 0=No, 1=Yes | Replaces # by %23 for some special situations. |
| `P20525`  | (val)  | Enable Connected Line ID                   | boolean | 0=No, 1=Yes |  |

---

### Port Settings > Port 1 > Advanced (`/portSetting/1/advance`)

**Request (frame 372):**
```
P198, P2318, P26015, P4340, P258, P2346, P243, P2311, P60082, P2367
```

**Response:**
| P-param   | Value  | Display Name                              | Type | Options/Range | Tooltip |
|-----------|--------|-------------------------------------------|------|------------|------------|
| `P198`    | `100`  | Special Feature                           | int |  | Specifies the server type for special requirements. |
| `P2318`   | `""`   | Conference URI                            | string |  | Configures the conference URI when using BroadSoft N-way calling feature. |
| `P26015`  | `0`    | Allow SIP Reset                           | int |  |  |
| `P4340`   | `0`    | Validate Incoming SIP Message             | boolean | 0=No, 1=Yes | Set whether to verify received SIP messages |
| `P258`    | `0`    | Check SIP User ID for Incoming INVITE     | boolean | 0=No, 1=Yes | If set to \ |
| `P2346`   | `0`    | Authenticate Incoming INVITE              | boolean | 0=No, 1=Yes |  |
| `P243`    | `0`    | Allow Incoming SIP Messages from SIP Proxy Only | boolean | 0=No, 1=Yes | Allow Incoming SIP Messages from SIP Proxy Only |
| `P2311`   | `0`    | Authenticate Server Certificate domain    | boolean | 0=No, 1=Yes | Configures whether the certificate's domain will be checked when TLS is used for SIP Transport. |
| `P60082`  | `""`   | Trusted Domain Name List                  | string |  |  |
| `P2367`   | `0`    | Authenticate Server Certificate chain     | boolean | 0=No, 1=Yes |  |

---

### Port Settings > Port 1 > Call Features (`/portSetting/1/callfeature`)

**Request (frame 380):**
```
P191, P24199, P24060, P24001..P24089 (call feature code table)
```

**Response:** This is a feature code table. `P191` = `1` (Call Features Settings). Each feature has an enable flag and a star-code:

| P-param   | Value   | Display Name                     | Type | Options/Range | Tooltip |
|-----------|---------|----------------------------------|------|------------|------------|
| `P191`    | `1`     | Call Features Settings           | int |  | When enabled, Do No Disturb, Call Forward and other call features can be used via the local feature codes on the device. Otherwise, the ITSP feature codes will be used. Enable All will override all... |
| `P24199`  | `0`     | Reset Call Features              | boolean | 0=No, 1=Yes | Whether to enable the reset call function |
| `P24060`  | `1`     | SRTP Feature                     | boolean | 0=No, 1=Yes | Whether to enable SRTP (Real-time Transport Protocol) |
| `P24001`  | `16`    | Enable SRTP call                 | int |  | Set the function code to enable SRTP (default value is 16) |
| `P24002`  | `17`    | Disable SRTP call                | int |  | Set the function code to disable SRTP (default value is 17) |
| `P24061`  | `1`     | SRTP per call Feature            | boolean | 0=No, 1=Yes | Whether to enable SRTP (Real-time Transport Protocol), only the current call is valid |
| `P24003`  | `18`    | Enable SRTP per call             | int |  | Set the function code to enable SRTP (the default value is 18), which is only valid for the current call |
| `P24004`  | `19`    | Disable SRTP per call            | int |  | Set the function code to disable SRTP (the default value is 19), which is only valid for the current call. |
| `P24062`  | `1`     | CID Feature                      | boolean | 0=No, 1=Yes | Whether to display user ID |
| `P24006`  | `31`    | Enable CID                       | int |  | Set to enable display of user ID function code (default value is 31) |
| `P24005`  | `30`    | Disable CID                      | int |  | Set to cancel display of user ID function code (default value is 30) |
| `P24065`  | `1`     | CID per call Feature             | boolean | 0=No, 1=Yes | Whether to display the user ID, it is only valid for the current call |
| `P24019`  | `82`    | Enable CID per call              | int |  | Set to enable display of user ID function code (default value is 82), only valid for the current call |
| `P24010`  | `67`    | Disable CID per call             | int |  | Set to cancel display of user ID function code (default value is 67), only valid for the current call |
| `P24063`  | `1`     | Direct IP Calling Feature        | boolean | 0=No, 1=Yes | Whether direct IP calling function is allowed |
| `P24007`  | `47`    | Direct IP Calling                | int |  | Set the function code for direct IP calls (default value is 47) |
| `P24064`  | `1`     | CW Feature                       | boolean | 0=No, 1=Yes | Enable or disable call waiting function |
| `P24009`  | `51`    | Enable CW                        | int |  | Set the function code to enable call waiting (default value is 51) |
| `P24008`  | `50`    | Disable CW                       | int |  | Set the function code to cancel call waiting (default value is 50) |
| `P24067`  | `1`     | CW per call Feature              | boolean | 0=No, 1=Yes | Enable or cancel the call waiting function, only the current call is valid |
| `P24013`  | `71`    | Enable CW per call               | int |  | Set the function code to enable call waiting (default value is 71), only valid for the current call |
| `P24012`  | `70`    | Disable CW per call              | int |  | Set the function code to cancel call waiting (default value is 70), only valid for the current call |
| `P24066`  | `1`     | Call Return Feature               | boolean | 0=No, 1=Yes | Whether to enable the pullback function |
| `P24011`  | `69`    | Call Return                       | int |  | Set the function code for callback (default value is 69) |
| `P24068`  | `1`     | Unconditional Forward Feature    | boolean | 0=No, 1=Yes | Enable or disable unconditional call forwarding |
| `P24014`  | `72`    | Enable Unconditional Forward     | int |  | Set the function code to enable unconditional call forwarding (default value is 72) |
| `P24015`  | `73`    | Disable Unconditional Forward    | int |  | Set the function code to cancel unconditional call forwarding (default value is 73) |
| `P24072`  | `1`     | Busy Forward Feature             | boolean | 0=No, 1=Yes | Whether to enable the call forwarding function when busy |
| `P24021`  | `90`    | Enable Busy Forward              | int |  | Set the function code to enable call forwarding when busy (default value is 90) |
| `P24022`  | `91`    | Disable Busy Forward             | int |  | Set the function code to cancel call forwarding when busy (default value is 91) |
| `P24073`  | `1`     | Delayed Forward Feature          | boolean | 0=No, 1=Yes | Whether to enable the function of transferring calls without answering |
| `P24023`  | `92`    | Enable Delayed Forward           | int |  | Set the function code to enable call transfer without answering (default value is 92) |
| `P24024`  | `93`    | Disable Delayed Forward          | int |  | Set the function code for canceling unanswered call transfer (default value is 93) |
| `P24069`  | `1`     | Paging Feature                   | boolean | 0=No, 1=Yes | Whether to enable the paging call function |
| `P24016`  | `74`    | Paging                           | int |  | Set the function code for paging calls (default value is 74) |
| `P24070`  | `1`     | DND Feature                      | boolean | 0=No, 1=Yes | Whether to enable the do not disturb function |
| `P24017`  | `78`    | Enable DND                       | int |  | Set the function code to enable the do not disturb function (default value is 78) |
| `P24018`  | `79`    | Disable DND                      | int |  | Set the function code to disable the do not disturb function (default value is 79) |
| `P24071`  | `1`     | Blind Transfer Feature           | int |  | Whether to enable blind transfer function |
| `P24020`  | `87`    | Enable Blind Transfer            | int |  | Set the blind transfer function code to start (default value is 87) |
| `P24074`  | `1`     | Disable LEC per call Feature     | boolean | 0=No, 1=Yes | Whether to disable the LEC function of the current call (only the current call is prohibited) |
| `P24025`  | `03`    | Disable LEC per call             | int |  | Set the function code to disable the LEC call function for the current call (default value is 03) |
| `P24087`  | `1`     | Play registration id Feature     | boolean | 0=No, 1=Yes | Whether to play registration ID |
| `P24038`  | `98`    | Enable playing registration id   | int |  | Set to enable the function code to play the registration ID (default value is 98) |
| `P24089`  | `1`     | Set Offhook Auto-Dial Feature    | boolean | 0=No, 1=Yes | Whether to Set Offhook Auto-Dial Feature |
| `P24040`  | `77`    | Enable set Offhook Auto-Dial     | int |  | Enable set Offhook Auto-Dial (default value is 77) |
| `P4830`   | `0`     | Enable Bellcore Style 3-Way Conference | boolean | 0=No, 1=Yes |  |
| `P24075`  | `1`     | Star Code 3WC Feature            | boolean | 0=No, 1=Yes | Star Code 3WC Feature |
| `P24026`  | `23`    | Star Code 3WC                    | int |  | Set the function code of the three-party conference (default value is 23) |
| `P24059`  | `1`     | Forced Codec Feature             | boolean | 0=No, 1=Yes | Whether to enable the function of forcing the speech encoding type |
| `P24000`  | `02`    | Forced Codec                     | int |  | Set the function code to enable forced voice coding type calls (default value is 02) |
| `P24076`  | `1`     | PCMU Codec Feature               | boolean | 0=No, 1=Yes | Whether to force PCMU speech encoding |
| `P24027`  | `7110`  | PCMU Codec                       | int |  | Set the function code to enable forced PCMU voice encoding calls (default value is 7110) |
| `P24077`  | `1`     | PCMA Codec Feature               | boolean | 0=No, 1=Yes | Whether to force PCMA voice encoding |
| `P24028`  | `7111`  | PCMA Codec                       | int |  | Set the function code to enable forced PCMA voice encoding (default value is 7111) |
| `P24078`  | `1`     | G723 Codec Feature               | boolean | 0=No, 1=Yes | Whether to force G723 speech encoding |
| `P24029`  | `723`   | G723 Codec                       | int |  | Set the function code to enable forced G723 speech encoding (default value is 723) |
| `P24079`  | `1`     | G729 Codec Feature               | boolean | 0=No, 1=Yes | Whether to force G729 speech encoding |
| `P24030`  | `729`   | G729 Codec                       | int |  | Set the function code to enable forced G729 speech encoding (default value is 729) |
| `P24084`  | `1`     | iLBC Codec Feature               | boolean | 0=No, 1=Yes | Whether to force iLBC voice encoding |
| `P24035`  | `7201`  | iLBC Codec                       | int |  | Set the function code to enable forced iLBC voice encoding (default value is 7201) |
| `P24085`  | `1`     | G722 Codec Feature               | boolean | 0=No, 1=Yes | Whether to force G722 speech encoding |
| `P24036`  | `722`   | G722 Codec                       | int |  | Set the function code to enable forced G722 codec voice encoding (The default value is 722) |

---

### Port Settings > Port 1 > Ring Tone (`/portSetting/1/tone`)

**Request (frame 388):**
```
P870, P871, P872, P873, P874, P875, P4010..P4019,
P29074..P29089
```

**Response:**
| P-param   | Value                         | Display Name                           | Type | Options/Range | Tooltip |
|-----------|-------------------------------|----------------------------------------|------|------------|------------|
| `P870`    | `0`                           | Custom Ring Tone 1                     | int |  | If the caller number matches, a custom ringtone will be used |
| `P871`    | `""`                          | Custom Ring Tone 1 will be used when the caller is | string |  | Set the caller ID using custom ringtone 1 |
| `P872`    | `0`                           | Custom Ring Tone 2                     | int |  | If the caller number matches, a custom ringtone will be used |
| `P873`    | `""`                          | Custom Ring Tone 2 will be used when the caller is | string |  | Set the caller ID using custom ringtone 2 |
| `P874`    | `0`                           | Custom Ring Tone 3                     | int |  | If the caller number matches, a custom ringtone will be used |
| `P875`    | `""`                          | Custom Ring Tone 3 will be used when the caller is | string |  | Set the caller ID using custom ringtone 3 |
| `P4010`   | `c=2000/4000;`               | Ring Tone 1                            | string |  | Syntax: c=on1/ off1[- on2/ off2[- on3/ off3]]; (melody on/off time must be a multiple of 1ms) |
| `P4011`   | `c=2000/4000;`               | Ring Tone 2                            | string |  | Syntax: c=on1/ off1[- on2/ off2[- on3/ off3]]; (melody on/off time must be a multiple of 1ms) |
| `P4012`   | `c=2000/4000;`               | Ring Tone 3                            | string |  | Syntax: c=on1/ off1[- on2/ off2[- on3/ off3]]; (melody on/off time must be a multiple of 1ms) |
| `P4013`   | `c=2000/4000;`               | Ring Tone 4                            | string |  | Syntax: c=on1/ off1[- on2/ off2[- on3/ off3]]; (melody on/off time must be a multiple of 1ms) |
| `P4014`   | `c=2000/4000;`               | Ring Tone 5                            | string |  | Syntax: c=on1/ off1[- on2/ off2[- on3/ off3]]; (melody on/off time must be a multiple of 1ms) |
| `P4015`   | `c=2000/4000;`               | Ring Tone 6                            | string |  | Syntax: c=on1/ off1[- on2/ off2[- on3/ off3]]; (melody on/off time must be a multiple of 1ms) |
| `P4016`   | `c=2000/4000;`               | Ring Tone 7                            | string |  | Syntax: c=on1/ off1[- on2/ off2[- on3/ off3]]; (melody on/off time must be a multiple of 1ms) |
| `P4017`   | `c=2000/4000;`               | Ring Tone 8                            | string |  | Syntax: c=on1/ off1[- on2/ off2[- on3/ off3]]; (melody on/off time must be a multiple of 1ms) |
| `P4018`   | `c=2000/4000;`               | Ring Tone 9                            | string |  | Syntax: c=on1/ off1[- on2/ off2[- on3/ off3]]; (melody on/off time must be a multiple of 1ms) |
| `P4019`   | `c=2000/4000;`               | Ring Tone 10                           | string |  | Syntax: c=on1/ off1[- on2/ off2[- on3/ off3]]; (melody on/off time must be a multiple of 1ms) |
| `P29074`  | `0`                           | Call Waiting Tone 1                    | int |  | If the caller number matches, a custom call waiting tone will be used |
| `P29077`  | `""`                          | Call Waiting Tone 1 used if incoming caller ID is | string |  | Set the incoming call number using custom call waiting tone 1 |
| `P29075`  | `0`                           | Call Waiting Tone 2                    | int |  | If the caller number matches, a custom call waiting tone will be used |
| `P29078`  | `""`                          | Call Waiting Tone 2 used if incoming caller ID is | string |  | Set the incoming call number using custom call waiting tone 2 |
| `P29076`  | `0`                           | Call Waiting Tone 3                    | int |  | If the caller number matches, a custom call waiting tone will be used |
| `P29079`  | `""`                          | Call Waiting Tone 3 used if incoming caller ID is | string |  | Set the incoming call number using custom call waiting tone 3 |
| `P29080`  | `f1=440@-13,c=300/10000;`    | Call Waiting Tone 1                    | string |  | Syntax: f1=val, f2=val[, c=on1/ off1[- on2/ off2[- on3/ off3]]]; (f is in Hz, on and off are calculated in 1ms. on is the ringing time , off is the silent time) |
| `P29081`  | `f1=440@-13,c=300/10000;`    | Call Waiting Tone 2                    | string |  | Syntax: f1=val, f2=val[, c=on1/ off1[- on2/ off2[- on3/ off3]]]; (f is in Hz, on and off are calculated in 1ms. on is the ringing time , off is the silent time) |
| `P29082`  | `f1=440@-13,c=300/10000;`    | Call Waiting Tone 3                    | string |  | Syntax: f1=val, f2=val[, c=on1/ off1[- on2/ off2[- on3/ off3]]]; (f is in Hz, on and off are calculated in 1ms. on is the ringing time , off is the silent time) |
| `P29083`  | `f1=440@-13,c=300/10000;`    | Call Waiting Tone 4                    | string |  | Syntax: f1=val, f2=val[, c=on1/ off1[- on2/ off2[- on3/ off3]]]; (f is in Hz, on and off are calculated in 1ms. on is the ringing time , off is the silent time) |
| `P29084`  | `f1=440@-13,c=300/10000;`    | Call Waiting Tone 5                    | string |  | Syntax: f1=val, f2=val[, c=on1/ off1[- on2/ off2[- on3/ off3]]]; (f is in Hz, on and off are calculated in 1ms. on is the ringing time , off is the silent time) |
| `P29085`  | `f1=440@-13,c=300/10000;`    | Call Waiting Tone 6                    | string |  | Syntax: f1=val, f2=val[, c=on1/ off1[- on2/ off2[- on3/ off3]]]; (f is in Hz, on and off are calculated in 1ms. on is the ringing time , off is the silent time) |
| `P29086`  | `f1=440@-13,c=300/10000;`    | Call Waiting Tone 7                    | string |  | Syntax: f1=val, f2=val[, c=on1/ off1[- on2/ off2[- on3/ off3]]]; (f is in Hz, on and off are calculated in 1ms. on is the ringing time , off is the silent time) |
| `P29087`  | `f1=440@-13,c=300/10000;`    | Call Waiting Tone 8                    | string |  | Syntax: f1=val, f2=val[, c=on1/ off1[- on2/ off2[- on3/ off3]]]; (f is in Hz, on and off are calculated in 1ms. on is the ringing time , off is the silent time) |
| `P29088`  | `f1=440@-13,c=300/10000;`    | Call Waiting Tone 9                    | string |  | Syntax: f1=val, f2=val[, c=on1/ off1[- on2/ off2[- on3/ off3]]]; (f is in Hz, on and off are calculated in 1ms. on is the ringing time , off is the silent time) |
| `P29089`  | `f1=440@-13,c=300/10000;`    | Call Waiting Tone 10                   | string |  | Syntax: f1=val, f2=val[, c=on1/ off1[- on2/ off2[- on3/ off3]]]; (f is in Hz, on and off are calculated in 1ms. on is the ringing time , off is the silent time) |

---

### Port Settings > Port 2 > General (`/portSetting/2/general`)

**Request (frame 398):**
```
P401, P747, P987, P4568, P748, P2433, P28097, P8618, P735, P736,
P703, P763, P5047, P5051, P702, P26140, P60156, P60155, P29195,
P2408, P2409, P2410, P730, P866, P792
```

Port 2 mirrors Port 1 general with offset P-parameter numbers.

**Response:**
| P-param   | Value  | Display Name                      | Type | Options/Range | Tooltip |
|-----------|--------|-----------------------------------|------|------------|------------|
| `P401`    | `0`    | Account Active                    | int |  | Indicates whether the account is active. |
| `P747`    | `""`   | Primary SIP Server                | string |  | The URL or IP address, and port of the SIP server. This is provided by your VoIP service provider (e.g., sip.mycompany.com, or IP address) |
| `P987`    | `""`   | Failover SIP Server               | string |  | Optional, used when primary server no response |
| `P4568`   | `0`    | Prefer Primary SIP Server         | enum | 0=No, 1=Will register to Primary Server if Failover registration expires, 2=W... |  |
| `P748`    | `""`   | Outbound Proxy                    | string |  | IP address or Domain name of the Primary Outbound Proxy, Media Gateway, or Session Border Controller. |
| `P2433`   | `""`   | Backup Outbound Proxy             | string |  | Defines secondary outbound proxy that will be used when the primary proxy cannot be connected. |
| `P28097`  | `0`    | Prefer Primary Outbound Proxy     | boolean | 0=No, 1=Yes | If set to yes, after expiration of registration, priority will be given to re-register with the primary proxy server. |
| `P8618`   | `""`   | From Domain                       | string |  | Optional, actual domain name, will override the from header |
| `P735`    | `""`   | SIP User ID                       |  |  | User account information, provided by your VoIP service provider. |
| `P736`    | `""`   | SIP Authenticate ID               |  |  | SIP service subscriber's Authenticate ID used for authentication. It can be identical to or different from the SIP User ID. |
| `P703`    | `""`   | Name                              |  |  | The SIP server subscriber's name (optional) that will be used for Caller ID display (e.g., John Doe). |
| `P763`    | `0`    | Tel URI                           | enum | 0=Disabled, 1=User=Phone, 2=Enabled |  |
| `P5047`   | `26`   | Layer 3 QoS SIP DSCP             | int |  | Diff-Serv value in decimal, 0-63, default 26 |
| `P5051`   | `46`   | Layer 3 QoS RTP DSCP             | int |  | Diff-Serv value in decimal, 0-63, default 46 |
| `P702`    | `0`    | DNS Mode                          | enum | 0=A, 1=SRV, 2=NAPTR/SRV, 3=Use Configured IP |  |
| `P26140`  | `0`    | DNS SRV Failover Mode             | enum | 0=Default, 1=Use current server until DNS TTL, 2=Use current server until no ... |  |
| `P60156`  | `60`   | Failback Timer                    | int |  | Specifies the duration (in minutes) since failover to the current SIP server or Outbound Proxy before making failback attempts to the primary SIP server or Outbound Proxy. Default is 60 minutes, wi... |
| `P60155`  | `2`    | Maximum Number of SIP Request Retries | int |  | Sets the maximum number of retries for the device to send requests to the server. If the destination address does not respond, all request messages are resent to the same address according to the c... |
| `P29195`  | `0`    | Register Before DNS SRV Failover  | boolean | 0=No, 1=Yes | Configures whether to send REGISTER requests to the failover SIP server or outbound proxy before sending INVITE requests in the event of a DNS SRV failover. |
| `P2408`   | `""`   | Primary IP                        | string |  |  |
| `P2409`   | `""`   | Backup IP 1                       | string |  |  |
| `P2410`   | `""`   | Backup IP 2                       | string |  |  |
| `P730`    | `0`    | NAT Traversal                     | enum | 0=No, 2=Keep-Alive, 1=STUN, 3=UPnP, 4=Auto, 5=VPN | Configures whether NAT traversal mechanism is activated. Please refer to user manual for more details. |
| `P866`    | `""`   | Use NAT IP                        | string |  | Configures the NAT IP address used in SIP/SDP messages. It should ONLY be used if required by your ITSP. |
| `P792`    | `""`   | Proxy-Require                     | string |  | Fill in the SIP proxy. This configuration is used to notify the SIP server that the device is behind NAT or a firewall. If you configure this, please ensure that the SIP server you are using suppor... |

---

### Port Settings > Port 2 > SIP (`/portSetting/2/sip`)

**Request (frame 426):**
```
P731, P830, P752, P813, P732, P2430, P471, P60196, P60197, P60198,
P26102, P28757, P28785, P2497, P2498, P2499, P709, P60168, P740,
P20502, P26103, P469, P4563, P489, P60181, P60180, P2429, P2431,
P4892, P2438, P2439, P26158, P26159, P29198, P4438, P440, P441,
P60174, P2487, P60175, P487, P435, P2459, P60164, P29171, P4835,
P26161, P29190, P95123, P2495, P434, P427, P428, P429, P430, P432,
P433, P431, P28745
```

Port 2 SIP settings mirror Port 1 with different P-values.

**Response (key fields):**
| P-param   | Value  | Display Name                                              | Type | Options/Range | Tooltip |
|-----------|--------|-----------------------------------------------------------|------|------------|------------|
| `P731`    | `1`    | SIP Registration                                          | boolean | 0=No, 1=Yes | Selects whether the device will send SIP REGISTER messages to the proxy/server. |
| `P830`    | `0`    | SIP Transport                                             | enum | 0=UDP, 1=TCP, 2=TLS | Set the network protocol used for SIP message transmission. |
| `P752`    | `0`    | Unregister On Reboot                                      | enum | 0=No, 1=All, 2=Instance |  |
| `P813`    | `1`    | Outgoing Call without Registration                        | boolean | 0=No, 1=Yes | Allow dialing without registering a SIP server |
| `P732`    | `60`   | Register Expiration                                       | int |  | Specifies the frequency (in minutes) in which the device refreshes its registration with the specified registrar. The maximum value is 64800 (about 45 days). |
| `P2430`   | `0`    | Re-Register before Expiration                             | int |  | Specifies the time frequency (in seconds) that the device sends re-registration request before the register expiration. Default is 0 second. Rang is 0-64800 (about 45 minutes). |
| `P471`    | `20`   | SIP Registration Failure Retry Wait Time                  | int |  | Specifies the interval (in seconds) to retry registration if the process failed. Default is 20 seconds. Valid range is 1 to 3600. |
| `P740`    | `5062` | Local SIP Port                                            | int |  | Configures the local SIP port used to listen and transmit. |
| `P489`    | `1`    | Support SIP Instance ID                                   | boolean | 0=No, 1=Yes | Configures whether SIP Instance ID is supported or not. |
| `P2429`   | `1`    | SIP URI Scheme When Using TLS                             | int |  |  |
| `P440`    | `50`   | SIP T1 Timeout                                            | enum | 50=0.5, 100=1, 200=2, 400=4, 800=8 | Set SIP T1 timeout, the default value is 0.5 seconds |
| `P441`    | `400`  | SIP T2 Timeout                                            | enum | 200=2, 400=4, 800=8, 1600=16, 3200=32 | Set SIP T2 timeout, the default value is 4 seconds |
| `P2487`   | `0`    | SIP Timer D                                               | int |  | 0 - 64 seconds. Default 0 |
| `P434`    | `180`  | Session Expiration                                        | int |  | Session Expiration is the time (in seconds) where the session is considered timed out, provided no successful session refresh transaction occurs beforehand. Default is 180 seconds. Range is 90-64800. |
| `P427`    | `90`   | Min-SE                                                    | int |  | The minimum session expiration (in seconds). Default is 90 seconds. Range is 90-64800. |
| `P428`    | `0`    | Caller Request Timer                                      | boolean | 0=No, 1=Yes |  |
| `P429`    | `0`    | Callee Request Timer                                      | boolean | 0=No, 1=Yes |  |
| `P430`    | `0`    | Force Timer                                               | boolean | 0=No, 1=Yes |  |
| `P432`    | `0`    | UAC Specify Refresher                                     | enum | 1=UAC, 2=UAS, 0=Omit(Recommended) |  |
| `P433`    | `1`    | UAS Specify Refresher                                     | enum | 1=UAC, 2=UAS | As a callee, select UAC to use caller or proxy server as the refresher, or select UAS to use the device as the refresher. |
| `P431`    | `0`    | Force INVITE                                              | boolean | 0=No, 1=Yes |  |
| `P28745`  | `0`    | When To Restart Session After Re-INVITE received          | enum | 0=Immediately, 1=After replying 200OK |  |
| `P739`    | `5012` | Local RTP Port                                            | int |  | Configures the local RTP port used to listen and transmit. Valid range is 1024 to 65535 and it must be even. |

---

### Port Settings > Port 2 > Codec (`/portSetting/2/codec`)

**Request (frame 438):**
```
P860, P861, P862, P28795, P28135, P28139, P779, P95107, P28773,
P28202, P28206, P28805, P28809, P28813, P28817, P4826, P28174, P28178,
P757, P758, P759, P760, P761, P762, P814, P815, P737, P749, P705,
P20530, P704, P2485, P26173, P26174, P26175, P750, P4364, P710,
P28914, P4417, P28924, P831, P832, P2463, P739, P20506, P60184, P60185,
P460, P2492, P28840, P443, P2483, P26193, P26194, P26195
```

Port 2 codec mirrors Port 1 codec with different P-values.

**Response (key fields):**
| P-param   | Value  | Display Name                                         | Type | Options/Range | Tooltip |
|-----------|--------|------------------------------------------------------|------|------------|------------|
| `P860`    | `101`  | Preferred DTMF                                       | int |  |  |
| `P861`    | `102`  | (Preferred Codec Choice 2)                           | int |  |  |
| `P862`    | `100`  | (Preferred Codec Choice 3)                           | int |  |  |
| `P28795`  | `0`    | Force DTMF to be sent via SIP INFO simultaneously   | int |  |  |
| `P779`    | `101`  | DTMF Payload Type                                    | int |  | Configures the payload type for DTMF using RFC2833. Cannot be the same as iLBC or Opus payload type. |
| `P95107`  | `0`    | Enable Multiple Sampling Rates in SDP telephone-event| int |  | Enable Multiple Sampling Rates in SDP telephone-event |
| `P28773`  | `6`    | Inband DTMF Tx Gain                                  | int |  | Range: -12-12 dB, default is 6 |
| `P28202`  | `30`   | DSP DTMF Detector Duration Threshold                 | int |  |  |
| `P28805`  | `-25`  | DSP DTMF Detector Min Level                          | int |  | Range: -45-0 dBm, default is -25 |
| `P28809`  | `1`    | DSP DTMF Detector Snr                                | int |  | Range: 0-12, default is 1 |
| `P28813`  | `25`   | DSP DTMF Detector Deviation                          | int |  | Range: 0-25, default is 25 |
| `P28817`  | `5`    | DSP DTMF Detector Twist                              | int |  | Range: 0-12dB, default is 5 |
| `P4826`   | `0`    | Enable DTMF Negotiation                              | int |  | If negotiaton is disabled, the above DTMF order will be used. |
| `P28174`  | `8`    | RFC2833 Events Count                                 | int |  | between 2 and 10, default is 8, 0 means continuous RFC2833 events |
| `P28178`  | `3`    | RFC2833 End Events Count                             | int |  | Between 2 and 10, the default value is 3 |
| `P757`    | `0`    | Vocoder Settings (1st)                               | int |  |  |
| `P758`    | `8`    | (Vocoder 2nd)                                        | int |  |  |
| `P759`    | `4`    | (Vocoder 3rd)                                        | int |  |  |
| `P760`    | `18`   | (Vocoder 4th)                                        | int |  |  |
| `P761`    | `2`    | (Vocoder 5th)                                        | int |  |  |
| `P762`    | `97`   | (Vocoder 6th)                                        | int |  |  |
| `P737`    | `2`    | Voice Frames per TX                                  | int |  |  |
| `P749`    | `0`    | G.723 Rate                                           | int |  | Selects encoding rate for G.723 codec. |
| `P705`    | `0`    | iLBC Frame Size                                      | int |  | Selects iLBC packet frame size. |
| `P704`    | `97`   | iLBC Payload Type                                    | int |  | Specifies iLBC payload type. Valid range is 96 to 127. Cannot be the same as Opus or DTMF payload type. |
| `P2485`   | `123`  | Opus Payload Type                                    | int |  | Specifies Opus payload type. Valid range is 96 to 127. It cannot be the same as iLBC or DTMF Payload Type. |
| `P750`    | `0`    | Silence Suppression                                  | boolean | 0=No, 1=Yes |  |
| `P4364`   | `0`    | Use First Matching Vocoder in 200OK SDP              | boolean | 0=No, 1=Yes | When enabled, the gateway will use the first matching code in 200OK SDP to make calls |
| `P710`    | `0`    | Fax Mode                                             | enum | 0=T.38, 1=Pass-Through | Fax Mode |
| `P28914`  | `2`    | T.38 Max Bit Rate                                    | enum | 1=4800bps, 2=9600bps, 3=14400bps | Selects the maximum T.38 bit rate.Lowering the maximum fax bit rate may help improve the fax success rate.<br/> Only effective when the fax machine is fax receipt. |
| `P4417`   | `1`    | Re-INVITE After Fax Tone Detected                    | boolean | 0=No, 1=Yes | Allow the device to issue a T.38 or fax pass re-invite if fax tones are detected. Enabled by default |
| `P28924`  | `0`    | Re-INVITE Upon CNG Count                             | int |  | 0: this feature is disabled; Equal to or greater than 1: ATA will initial Re-Invite request when CNG count is reached; The valid range is [0, 6]. |
| `P831`    | `1`    | Jitter Buffer Type                                   | enum | 0=Fixed, 1=Adaptive | Selects either Fixed or Adaptive based on network conditions. |
| `P832`    | `1`    | Jitter Buffer Length                                  | int |  | Selects Low, Medium, or High based on network conditions. |
| `P2463`   | `1`    | Crypto Life Time                                     | boolean | 0=No, 1=Yes | Configures whether to enable Crypto Life Time. |
| `P739`    | `5012` | Local RTP Port                                       | int |  | Configures the local RTP port used to listen and transmit. Valid range is 1024 to 65535 and it must be even. |
| `P20506`  | `0`    | Use Random RTP Port                                  | boolean | 0=No, 1=Yes | Use a random RTP port instead of the above set port |
| `P460`    | `0`    | Symmetric RTP                                        | boolean | 0=No, 1=Yes |  |
| `P2492`   | `1`    | Enable RTCP                                          | boolean | 0=No, 1=Yes | Allow users to enable RTCP |
| `P28840`  | `0`    | RTP/RTCP Keep Alive On Hold                          | boolean | 0=No, 1=Yes | RTP/RTCP Keep Alive On Hold |
| `P443`    | `0`    | SRTP Mode                                            | int |  | Enables and selects SRTP mode. |
| `P2483`   | `0`    | SRTP Key Length                                      | int |  | The cipher method/key length to use if SRTP is enabled. |
| `P26193`  | `""`   | VQ RTCP-XR Collector Name                            | string |  | Configures the host name of the central report collector that accepts voice quality reports contained in SIP PUBLISH messages. |
| `P26194`  | `""`   | VQ RTCP-XR Collector Address                         | string |  | Configures the IP address of the central report collector that accepts voice quality reports contained in SIP PUBLISH messages. |
| `P26195`  | `5060` | VQ RTCP-XR Collector Port                            | int |  | Configures the port of the central report collector that accepts voice quality reports contained in SIP PUBLISH messages. |

---

### Port Settings > Port 2 > Analog Line (`/portSetting/2/analogline`)

**Request:**
```
P864, P863, P4663, P4664, P865, P893, P21926, P857, P20522,
P28166, P4425, P811, P812, P834, P248, P283, P825, P4430, P4235, P28193
```

**Response:**
| P-param   | Value  | Display Name                                          | Type | Options/Range | Tooltip |
|-----------|--------|-------------------------------------------------------|------|------------|------------|
| `P864`    | `0`    | Analog Signal Line Configuration                      | int |  | Select the impedance used by the PSTN service provider |
| `P863`    | `0`    | Caller ID Scheme                                      | int |  | Select caller ID mechanism |
| `P4663`   | `0`    | DTMF Caller ID                                        | int |  |  |
| `P4664`   | `0`    | (Rx Mute)                                             | int |  |  |
| `P865`    | `0`    | Polarity Reversal                                     | int |  | Reverse polarity upon call establishment and termination |
| `P893`    | `0`    | Loop Current Disconnect                               | boolean | 0=No, 1=Yes | Loop current disconnect upon call termination |
| `P21926`  | `0`    | Play busy/reorder tone before Loop Current Disconnect | int |  | Play busy/reorder tone before loop current disconnect upon call fail |
| `P857`    | `200`  | Loop Current Disconnect Duration                      | int |  | 100 - 10000 milliseconds. Default 200 milliseconds |
| `P20522`  | `0`    | Enable Pulse Dialing                                  | int |  |  |
| `P28166`  | `0`    | Pulse Dialing Standard                                | enum | 0=General Standard, 1=Swedish Standard, 2=New Zealand Standard | Pulse Dialing Standard |
| `P4425`   | `1`    | Enable Hook Flash                                     | int |  |  |
| `P811`    | `300`  | Hook Flash Timing                                     | int |  |  |
| `P812`    | `1100` | (On-hook timer)                                       | int |  |  |
| `P834`    | `400`  | On Hook Timing                                        | int |  | In 40-2000 milliseconds range, default is 400 |
| `P248`    | `0`    | Gain                                                  | int |  |  |
| `P283`    | `6`    | (Number setting)                                      | int |  |  |
| `P825`    | `0`    | Enable Line Echo Canceller (LEC)                      | boolean | 0=No, 1=Yes |  |
| `P4430`   | `20`   | Ring Frequency                                        | int |  | Selects ringing frequency settings |
| `P4235`   | `0`    | Ring Power                                            | int |  | Selects ringing power settings |
| `P28193`  | `2`    | OnHook DC Feed Current                                | int |  | Selects the DC feed current under on-hook |

---

### Port Settings > Port 2 > Call Settings (`/portSetting/2/call`)

**Request:**
```
P771, P4046, P292, P729, P766, P4201, P772, P28148, P26162, P791,
P823, P817, P765, P446, P4421, P28761, P4794, P4361, P29172,
P869, P4372, P28198, P4561, P4821, P470, P774, P28081, P28170,
P816, P2424, P28154, P29173, P29196, P4895, P20526
```

**Response:**
| P-param   | Value                              | Display Name                               | Type | Options/Range | Tooltip |
|-----------|------------------------------------|--------------------------------------------|------|------------|------------|
| `P771`    | `""`                               | Off-hook Auto Dial                         |  |  | User ID/extension to dial automatically when offhook |
| `P4046`   | `0`                                | Offhook Auto-Dial Delay                    | int |  | 0-60 seconds, default is 0 |
| `P292`    | `4`                                | Inter-Digit Timeout (sec)                  | int |  | Configures the timeout (in seconds) for no key entry. If no key is pressed after the timeout, the collected digits will be sent out. |
| `P729`    | `0`                                | Early Dial                                 | boolean | 0=No, 1=Yes |  |
| `P766`    | `""`                               | Dial Plan Prefix                           | string |  | Configures a prefix added to all numbers when making outbound calls. |
| `P4201`   | `{ x+ \| \\+x+ \| *x+ \| *xx*x+ }` | Dial Plan                                | string |  | Set gateway dialing rules. Please refer to the user manual for specific syntax and examples |
| `P772`    | `1`                                | Use # as Dial Key                          | boolean | 0=No, 1=Yes |  |
| `P28148`  | `0`                                | Enable # as Redial Key                     | int |  |  |
| `P26162`  | `1`                                | RFC2543 Hold                               | int |  |  |
| `P791`    | `0`                                | Enable Call-Waiting                        | int |  |  |
| `P823`    | `0`                                | Enable Call-Waiting Caller ID              | int |  |  |
| `P817`    | `0`                                | Enable Call-Waiting Tone                   | int |  |  |
| `P765`    | `0`                                | Send Anonymous                             | int |  |  |
| `P446`    | `0`                                | Anonymous Call Rejection                   | boolean | 0=No, 1=Yes |  |
| `P4421`   | `0`                                | Outgoing Call Duration Limit               | int |  | 0-180 minutes, default is 0 (No Limit) |
| `P28761`  | `0`                                | Incoming Call Duration Limit               | int |  | 0-180 minutes, default is 0 (No Limit) |
| `P4794`   | `0`                                | Enable Receiver Offhook Tone               | int |  |  |
| `P4361`   | `0`                                | Enable Reminder Ring for On-Hold Call      | int |  |  |
| `P29172`  | `1`                                | Enable Reminder Ring for DND               | int |  |  |
| `P869`    | `0`                                | Enable Visual MWI                          | int |  |  |
| `P4372`   | `1`                                | Visual MWI Type                            | int |  | Configure the type of message waiting prompt (MWI) |
| `P28198`  | `0`                                | MWI Tone                                   | int |  | MWI Tone |
| `P4561`   | `0`                                | Transfer on Conference Hangup              | int |  |  |
| `P4821`   | `0`                                | Ringing Transfer                           | int |  | Defines whether the call is transferred to the other party When the transferring party hangs up while listening to the ringback tone. |
| `P470`    | `20`                               | No Answer Timeout                          | int |  | Defines the timeout (in seconds) before the call is forwarded on no answer. Valid range is 1 to 120. |
| `P774`    | `0`                                | Send Hook Flash Event                      | int |  | Hook Flash will be sent as a DTMF event if set to Yes |
| `P28081`  | `0`                                | Flash Digit Control                        | boolean | 0=No, 1=Yes | Overrides the default settings for call control when both channels are in use |
| `P28170`  | `0`                                | Callee Flash to 3WC                        | boolean | 0=No, 1=Yes | In call waiting scenarios, hookflash switches between two calls by default. After turning on the option, enter a three-party conference |
| `P816`    | `60`                               | Ring Timeout                               | int |  |  |
| `P2424`   | `0`                                | Caller ID Display                          | int |  |  |
| `P28154`  | `0`                                | Enable Unknown Caller ID                   | int |  |  |
| `P29173`  | `0`                                | Replace Beginning '+' with 00 in Caller ID | boolean | 0=No, 1=Yes | Replace Beginning '+' with 00 in Caller ID |
| `P29196`  | `0`                                | Number of Beginning Digits to Strip from Caller ID | int |  |  |
| `P4895`   | `0`                                | Escape '#' as %23 in SIP URI               | boolean | 0=No, 1=Yes | Replaces # by %23 for some special situations. |
| `P20526`  | `0`                                | Enable Connected Line ID                   | int |  |  |

---

### Port Settings > Port 2 > Advanced (`/portSetting/2/advance`)

**Request:**
```
P767, P2418, P26115, P4341, P449, P2446, P743, P2411, P60182, P2467
```

**Response:**
| P-param   | Value  | Display Name                              | Type | Options/Range | Tooltip |
|-----------|--------|-------------------------------------------|------|------------|------------|
| `P767`    | `100`  | Special Feature                           | int |  | Specifies the server type for special requirements. |
| `P2418`   | `""`   | Conference URI                            |  |  |  |
| `P26115`  | `0`    | Allow SIP Reset                           | int |  |  |
| `P4341`   | `0`    | Validate Incoming SIP Message             | boolean | 0=No, 1=Yes | Set whether to verify received SIP messages |
| `P449`    | `0`    | Check SIP User ID for Incoming INVITE     | boolean | 0=No, 1=Yes | If set to \ |
| `P2446`   | `0`    | Authenticate Incoming INVITE              | boolean | 0=No, 1=Yes |  |
| `P743`    | `0`    | Allow Incoming SIP Messages from SIP Proxy Only | boolean | 0=No, 1=Yes | Allow Incoming SIP Messages from SIP Proxy Only |
| `P2411`   | `0`    | Authenticate Server Certificate domain    | boolean | 0=No, 1=Yes | Configures whether the certificate's domain will be checked when TLS is used for SIP Transport. |
| `P60182`  | `""`   | Trusted Domain Name List                  | string |  |  |
| `P2467`   | `0`    | Authenticate Server Certificate chain     | boolean | 0=No, 1=Yes |  |

---

### Port Settings > Port 2 > Call Features (`/portSetting/2/callfeature`)

**Request (frame 1119 from capture 3):**
```
P751, P24399, P24260, P24201, P24202, P24261, P24203, P24204,
P24262, P24206, P24205, P24265, P24219, P24210, P24263, P24207,
P24264, P24209, P24208, P24267, P24213, P24212, P24266, P24211,
P24268, P24214, P24215, P24272, P24221, P24222, P24273, P24223,
P24224, P24269, P24216, P24270, P24217, P24218, P24271, P24220,
P24274, P24225, P24289, P24240, P24287, P24238, P4831, P24275,
P24226, P24259, P24200, P24276, P24227, P24277, P24228, P24278,
P24229, P24279, P24230, P24284, P24235, P24285, P24236
```

Port 2 call features mirror Port 1 with offset P-numbers (P24000→P24200, P24060→P24260, etc.).

**Response:**
| P-param   | Value   | Display Name                     | Type | Options/Range | Tooltip |
|-----------|---------|----------------------------------|------|------------|------------|
| `P751`    | `1`     | Enable Local Call Features       | boolean | 0=No, 1=Yes | When enabled, Do No Disturb, Call Forward and other call features can be used via the local feature codes on the device. Otherwise, the ITSP feature codes will be used. Enable All will override all... |
| `P24399`  | `0`     | Reset Call Features              | boolean | 0=No, 1=Yes | Whether to enable the reset call function |
| `P24260`  | `1`     | SRTP Feature                     | boolean | 0=No, 1=Yes | Whether to enable SRTP (Real-time Transport Protocol) |
| `P24201`  | `16`    | Enable SRTP call                 | string |  | Set the function code to enable SRTP (default value is 16) |
| `P24202`  | `17`    | Disable SRTP call                | string |  | Set the function code to disable SRTP (default value is 17) |
| `P24261`  | `1`     | SRTP per call Feature            | boolean | 0=No, 1=Yes | Whether to enable SRTP (Real-time Transport Protocol), only the current call is valid |
| `P24203`  | `18`    | Enable SRTP per call             | string |  | Set the function code to enable SRTP (the default value is 18), which is only valid for the current call |
| `P24204`  | `19`    | Disable SRTP per call            | string |  | Set the function code to disable SRTP (the default value is 19), which is only valid for the current call. |
| `P24262`  | `1`     | CID Feature                      | boolean | 0=No, 1=Yes | Whether to display user ID |
| `P24206`  | `31`    | Enable CID                       | string |  | Set to enable display of user ID function code (default value is 31) |
| `P24205`  | `30`    | Disable CID                      | string |  | Set to cancel display of user ID function code (default value is 30) |
| `P24265`  | `1`     | CID per call Feature             | boolean | 0=No, 1=Yes | Whether to display the user ID, it is only valid for the current call |
| `P24219`  | `82`    | Enable CID per call              | string |  | Set to enable display of user ID function code (default value is 82), only valid for the current call |
| `P24210`  | `67`    | Disable CID per call             | string |  | Set to cancel display of user ID function code (default value is 67), only valid for the current call |
| `P24263`  | `1`     | Direct IP Calling Feature        | boolean | 0=No, 1=Yes | Whether direct IP calling function is allowed |
| `P24207`  | `47`    | Direct IP Calling                | string |  | Set the function code for direct IP calls (default value is 47) |
| `P24264`  | `1`     | CW Feature                       | boolean | 0=No, 1=Yes | Enable or disable call waiting function |
| `P24209`  | `51`    | Enable CW                        | string |  | Set the function code to enable call waiting (default value is 51) |
| `P24208`  | `50`    | Disable CW                       | string |  | Set the function code to cancel call waiting (default value is 50) |
| `P24267`  | `1`     | CW per call Feature              | boolean | 0=No, 1=Yes | Enable or cancel the call waiting function, only the current call is valid |
| `P24213`  | `71`    | Enable CW per call               | string |  | Set the function code to enable call waiting (default value is 71), only valid for the current call |
| `P24212`  | `70`    | Disable CW per call              | string |  | Set the function code to cancel call waiting (default value is 70), only valid for the current call |
| `P24266`  | `1`     | Call Return Feature              | boolean | 0=No, 1=Yes | Whether to enable the pullback function |
| `P24211`  | `69`    | Call Return                      | string |  | Set the function code for callback (default value is 69) |
| `P24268`  | `1`     | Unconditional Forward Feature    | boolean | 0=No, 1=Yes | Enable or disable unconditional call forwarding |
| `P24214`  | `72`    | Enable Unconditional Forward     | string |  | Set the function code to enable unconditional call forwarding (default value is 72) |
| `P24215`  | `73`    | Disable Unconditional Forward    | string |  | Set the function code to cancel unconditional call forwarding (default value is 73) |
| `P24272`  | `1`     | Busy Forward Feature             | boolean | 0=No, 1=Yes | Whether to enable the call forwarding function when busy |
| `P24221`  | `90`    | Enable Busy Forward              | string |  | Set the function code to enable call forwarding when busy (default value is 90) |
| `P24222`  | `91`    | Disable Busy Forward             | string |  | Set the function code to cancel call forwarding when busy (default value is 91) |
| `P24273`  | `1`     | Delayed Forward Feature          | boolean | 0=No, 1=Yes | Whether to enable the function of transferring calls without answering |
| `P24223`  | `92`    | Enable Delayed Forward           | string |  | Set the function code to enable call transfer without answering (default value is 92) |
| `P24224`  | `93`    | Disable Delayed Forward          | string |  | Set the function code for canceling unanswered call transfer (default value is 93) |
| `P24269`  | `1`     | Paging Feature                   | boolean | 0=No, 1=Yes | Whether to enable the paging call function |
| `P24216`  | `74`    | Paging                           | string |  | Set the function code for paging calls (default value is 74) |
| `P24270`  | `1`     | DND Feature                      | boolean | 0=No, 1=Yes | Whether to enable the do not disturb function |
| `P24217`  | `78`    | Enable DND                       | string |  | Set the function code to enable the do not disturb function (default value is 78) |
| `P24218`  | `79`    | Disable DND                      | string |  | Set the function code to disable the do not disturb function (default value is 79) |
| `P24271`  | `1`     | Blind Transfer Feature           | boolean | 0=No, 1=Yes | Whether to enable blind transfer function |
| `P24220`  | `87`    | Enable Blind Transfer            | string |  | Set the blind transfer function code to start (default value is 87) |
| `P24274`  | `1`     | Disable LEC per call Feature     | boolean | 0=No, 1=Yes | Whether to disable the LEC function of the current call (only the current call is prohibited) |
| `P24225`  | `03`    | Disable LEC per call             | string |  | Set the function code to disable the LEC call function for the current call (default value is 03) |
| `P24289`  | `1`     | Set Offhook Auto-Dial Feature    | boolean | 0=No, 1=Yes |  |
| `P24240`  | `77`    | Enable set Offhook Auto-Dial     | string |  |  |
| `P24287`  | `1`     | Play registration id Feature     | boolean | 0=No, 1=Yes | Whether to play registration ID |
| `P24238`  | `98`    | Enable playing registration id   | string |  | Set to enable the function code to play the registration ID (default value is 98) |
| `P4831`   | `0`     | Enable Bellcore Style 3-Way Conference | boolean | 0=No, 1=Yes |  |
| `P24275`  | `1`     | Star Code 3WC Feature            | boolean | 0=No, 1=Yes | Star Code 3WC Feature |
| `P24226`  | `23`    | Star Code 3WC                    | string |  | Set the function code of the three-party conference (default value is 23) |
| `P24259`  | `1`     | Forced Codec Feature             | boolean | 0=No, 1=Yes | Whether to enable the function of forcing the speech encoding type |
| `P24200`  | `02`    | Forced Codec                     | string |  | Set the function code to enable forced voice coding type calls (default value is 02) |
| `P24276`  | `1`     | PCMU Codec Feature               | boolean | 0=No, 1=Yes | Whether to force PCMU speech encoding |
| `P24227`  | `7110`  | PCMU Codec                       | string |  | Set the function code to enable forced PCMU voice encoding calls (default value is 7110) |
| `P24277`  | `1`     | PCMA Codec Feature               | boolean | 0=No, 1=Yes | Whether to force PCMA voice encoding |
| `P24228`  | `7111`  | PCMA Codec                       | string |  | Set the function code to enable forced PCMA voice encoding (default value is 7111) |
| `P24278`  | `1`     | G723 Codec Feature               | boolean | 0=No, 1=Yes | Whether to force G723 speech encoding |
| `P24229`  | `723`   | G723 Codec                       | string |  | Set the function code to enable forced G723 speech encoding (default value is 723) |
| `P24279`  | `1`     | G729 Codec Feature               | boolean | 0=No, 1=Yes | Whether to force G729 speech encoding |
| `P24230`  | `729`   | G729 Codec                       | string |  | Set the function code to enable forced G729 speech encoding (default value is 729) |
| `P24284`  | `1`     | iLBC Codec Feature               | boolean | 0=No, 1=Yes | Whether to force iLBC voice encoding |
| `P24235`  | `7201`  | iLBC Codec                       | string |  | Set the function code to enable forced iLBC voice encoding (default value is 7201) |
| `P24285`  | `1`     | G722 Codec Feature               | boolean | 0=No, 1=Yes | Whether to force G722 speech encoding |
| `P24236`  | `722`   | G722 Codec                       | string |  | Set the function code to enable forced G722 codec voice encoding (The default value is 722) |

---

### Port Settings > Port 2 > Ring Tone (`/portSetting/2/tone`)

**Request (frame 1131 from capture 3):**
```
P880, P881, P882, P883, P884, P885, P4030..P4039,
P29174..P29189
```

Port 2 tone mirrors Port 1 with offset P-numbers (P870→P880, P4010→P4030, P29074→P29174, etc.).

**Response:**
| P-param   | Value                         | Display Name                    | Type | Options/Range | Tooltip |
|-----------|-------------------------------|---------------------------------|------|------------|------------|
| `P880`    | `0`                           | Custom Ring Tone 1              | boolean | 0=No, 1=Yes | If the caller number matches, a custom ringtone will be used |
| `P881`    | `""`                          | Custom Ring Tone 1 will be used when the caller is | string |  | Set the caller ID using custom ringtone 1 |
| `P882`    | `0`                           | Custom Ring Tone 2              | boolean | 0=No, 1=Yes | If the caller number matches, a custom ringtone will be used |
| `P883`    | `""`                          | Custom Ring Tone 2 will be used when the caller is | string |  | Set the caller ID using custom ringtone 2 |
| `P884`    | `0`                           | Custom Ring Tone 3              | boolean | 0=No, 1=Yes | If the caller number matches, a custom ringtone will be used |
| `P885`    | `""`                          | Custom Ring Tone 3 will be used when the caller is | string |  | Set the caller ID using custom ringtone 3 |
| `P4030`   | `c=2000/4000;`               | Ring Tone 1                     | string |  | Syntax: c=on1/ off1[- on2/ off2[- on3/ off3]]; (melody on/off time must be a multiple of 1ms) |
| `P4031`   | `c=2000/4000;`               | Ring Tone 2                     | string |  | Syntax: c=on1/ off1[- on2/ off2[- on3/ off3]]; (melody on/off time must be a multiple of 1ms) |
| `P4032`   | `c=2000/4000;`               | Ring Tone 3                     | string |  | Syntax: c=on1/ off1[- on2/ off2[- on3/ off3]]; (melody on/off time must be a multiple of 1ms) |
| `P4033`   | `c=2000/4000;`               | Ring Tone 4                     | string |  | Syntax: c=on1/ off1[- on2/ off2[- on3/ off3]]; (melody on/off time must be a multiple of 1ms) |
| `P4034`   | `c=2000/4000;`               | Ring Tone 5                     | string |  | Syntax: c=on1/ off1[- on2/ off2[- on3/ off3]]; (melody on/off time must be a multiple of 1ms) |
| `P4035`   | `c=2000/4000;`               | Ring Tone 6                     | string |  | Syntax: c=on1/ off1[- on2/ off2[- on3/ off3]]; (melody on/off time must be a multiple of 1ms) |
| `P4036`   | `c=2000/4000;`               | Ring Tone 7                     | string |  | Syntax: c=on1/ off1[- on2/ off2[- on3/ off3]]; (melody on/off time must be a multiple of 1ms) |
| `P4037`   | `c=2000/4000;`               | Ring Tone 8                     | string |  | Syntax: c=on1/ off1[- on2/ off2[- on3/ off3]]; (melody on/off time must be a multiple of 1ms) |
| `P4038`   | `c=2000/4000;`               | Ring Tone 9                     | string |  | Syntax: c=on1/ off1[- on2/ off2[- on3/ off3]]; (melody on/off time must be a multiple of 1ms) |
| `P4039`   | `c=2000/4000;`               | Ring Tone 10                    | string |  | Syntax: c=on1/ off1[- on2/ off2[- on3/ off3]]; (melody on/off time must be a multiple of 1ms) |
| `P29174`  | `0`                           | Call Waiting Tone 1             | boolean | 0=No, 1=Yes | If the caller number matches, a custom call waiting tone will be used |
| `P29177`  | `""`                          | Call Waiting Tone 1 used if incoming caller ID is | string |  | Set the incoming call number using custom call waiting tone 1 |
| `P29175`  | `0`                           | Call Waiting Tone 2             | boolean | 0=No, 1=Yes | If the caller number matches, a custom call waiting tone will be used |
| `P29178`  | `""`                          | Call Waiting Tone 2 used if incoming caller ID is | string |  | Set the incoming call number using custom call waiting tone 2 |
| `P29176`  | `0`                           | Call Waiting Tone 3             | boolean | 0=No, 1=Yes | If the caller number matches, a custom call waiting tone will be used |
| `P29179`  | `""`                          | Call Waiting Tone 3 used if incoming caller ID is | string |  | Set the incoming call number using custom call waiting tone 3 |
| `P29180`  | `f1=440@-13,c=300/10000;`    | Call Waiting Tone 1             | string |  | Syntax: f1=val, f2=val[, c=on1/ off1[- on2/ off2[- on3/ off3]]]; (f is in Hz, on and off are calculated in 1ms. on is the ringing time , off is the silent time) |
| `P29181`  | `f1=440@-13,c=300/10000;`    | Call Waiting Tone 2             | string |  | Syntax: f1=val, f2=val[, c=on1/ off1[- on2/ off2[- on3/ off3]]]; (f is in Hz, on and off are calculated in 1ms. on is the ringing time , off is the silent time) |
| `P29182`  | `f1=440@-13,c=300/10000;`    | Call Waiting Tone 3             | string |  | Syntax: f1=val, f2=val[, c=on1/ off1[- on2/ off2[- on3/ off3]]]; (f is in Hz, on and off are calculated in 1ms. on is the ringing time , off is the silent time) |
| `P29183`  | `f1=440@-13,c=300/10000;`    | Call Waiting Tone 4             | string |  | Syntax: f1=val, f2=val[, c=on1/ off1[- on2/ off2[- on3/ off3]]]; (f is in Hz, on and off are calculated in 1ms. on is the ringing time , off is the silent time) |
| `P29184`  | `f1=440@-13,c=300/10000;`    | Call Waiting Tone 5             | string |  | Syntax: f1=val, f2=val[, c=on1/ off1[- on2/ off2[- on3/ off3]]]; (f is in Hz, on and off are calculated in 1ms. on is the ringing time , off is the silent time) |
| `P29185`  | `f1=440@-13,c=300/10000;`    | Call Waiting Tone 6             | string |  | Syntax: f1=val, f2=val[, c=on1/ off1[- on2/ off2[- on3/ off3]]]; (f is in Hz, on and off are calculated in 1ms. on is the ringing time , off is the silent time) |
| `P29186`  | `f1=440@-13,c=300/10000;`    | Call Waiting Tone 7             | string |  | Syntax: f1=val, f2=val[, c=on1/ off1[- on2/ off2[- on3/ off3]]]; (f is in Hz, on and off are calculated in 1ms. on is the ringing time , off is the silent time) |
| `P29187`  | `f1=440@-13,c=300/10000;`    | Call Waiting Tone 8             | string |  | Syntax: f1=val, f2=val[, c=on1/ off1[- on2/ off2[- on3/ off3]]]; (f is in Hz, on and off are calculated in 1ms. on is the ringing time , off is the silent time) |
| `P29188`  | `f1=440@-13,c=300/10000;`    | Call Waiting Tone 9             | string |  | Syntax: f1=val, f2=val[, c=on1/ off1[- on2/ off2[- on3/ off3]]]; (f is in Hz, on and off are calculated in 1ms. on is the ringing time , off is the silent time) |
| `P29189`  | `f1=440@-13,c=300/10000;`    | Call Waiting Tone 10            | string |  | Syntax: f1=val, f2=val[, c=on1/ off1[- on2/ off2[- on3/ off3]]]; (f is in Hz, on and off are calculated in 1ms. on is the ringing time , off is the silent time) |

---

### Maintenance > Upgrade > Firmware (`/maintenance/upgrade/firmware`)

**Request (frame 449):**
```
P6767, P192, P6768, P6769, P232, P233
```

**Also fetches MAC (frame 454).**

**Response:**
| P-param  | Value                      | Display Name                     | Type | Options/Range | Tooltip |
|----------|----------------------------|----------------------------------|------|------------|------------|
| `P6767`  | `2`                        | Firmware Upgrade via             | enum | 0=TFTP, 1=HTTP, 2=HTTPS, 3=FTP, 4=FTPS | Allows users to choose the firmware upgrade method via TFTP, HTTP, HTTPS, FTP or FTPS. |
| `P192`   | `fm.grandstream.com/gs`    | Firmware Server Path             | string |  | Defines the server path for the firmware server. |
| `P6768`  | `""`                       | Firmware Server Username         | string |  | The username for the firmware server. |
| `P6769`  | `""`                       | Firmware Server Password         | string (password) |  | The password for the firmware server. |
| `P232`   | `""`                       | Firmware File Prefix             | string |  | If configured, only the firmware with the matching prefix will be downloaded and written to the device. |
| `P233`   | `""`                       | Firmware File Postfix            | string |  | If configured, only the firmware with the matching postfix will be downloaded and written to the device. |

---

### Maintenance > Upgrade > Config (`/maintenance/upgrade/config`)

**Request (frame 462 / 467):**
```
P212, P237, P1360, P1361, P1359, P234, P235, P20713, P240
```

**Response:**
| P-param   | Value                     | Display Name                          | Type | Options/Range | Tooltip |
|-----------|---------------------------|---------------------------------------|------|------------|------------|
| `P212`    | `2`                       | Config File                           | int |  | Allows users to choose the config upgrade method via TFTP, HTTP, HTTPS, FTP or FTPS. |
| `P237`    | `fm.grandstream.com/gs`   | Config Server Path                    | string |  | Defines the server path for provisioning. |
| `P1360`   | `""`                      | Config Server Username                |  |  | The username for the config server. |
| `P1361`   | `""`                      | Config Server Password                |  |  | The password for the config server. |
| `P1359`   | `""`                      | XML Config File Password              |  |  | Configures the password for encrypting the XML configuration file using OpenSSL. This is required for the device to decrypt the encrypted XML configuration file. |
| `P234`    | `""`                      | Config File Prefix                    |  |  | If configured, only the configuration file with the matching encrypted prefix will be downloaded and written to the device. |
| `P235`    | `""`                      | Config File Postfix                   |  |  | If configured, only the configuration file with the matching encrypted postfix will be downloaded and written to the device. |
| `P20713`  | `0`                       | Always Authenticate before Challenge  | boolean | 0=No, 1=Yes | If enabled, the device will send credentials before being challenged by the server. This option only applies to HTTP/HTTPS. |
| `P240`    | `0`                       | Authenticate Conf File                | boolean | 0=No, 1=Yes | If enabled, the device will authenticate the configuration file before acceptance. |

---

### Maintenance > Upgrade > Deploy (`/maintenance/upgrade/deploy`)

**Request (frame 559):**
```
P145, P1414, P8609, P8337, P22296, P286, P285, P8459, P193,
P8458, P238, P8467, P8501
```

**Response:**
| P-param   | Value                                    | Display Name                            | Type | Options/Range | Tooltip |
|-----------|------------------------------------------|-----------------------------------------|------|------------|------------|
| `P145`    | `1`                                      | Provision                               | boolean | 0=No, 1=Yes | When enabled, the upgrade method and the server path of the firmware/config provisioning will be reset according to option 43/66/160 sent by the DHCP server |
| `P1414`   | `1`                                      | Auto Provision                          | boolean | 0=No, 1=Yes | When enabled, the device sends SUBSCRIBE in multicast mode. If 3CX, UCM and other IPPBX servers are used as SIP servers, the device can be automatically configured. |
| `P8609`   | `0`                                      | Enable using tags in URL                | boolean | 0=No, 1=Yes | Enable the use of labels in profile server paths |
| `P8337`   | `0`                                      | Additional Override DHCP Option         | enum | 0=none, 1=Option 150 | Configures additional DHCP Option to be used for firmware/config server instead of the configured firmware/config server or the server from DHCP Option 66 and 160. |
| `P22296`  | `0`                                      | Automatic Upgrade                       | enum | 0=No, 1=Check at a Period of Time, 2=Check Every Day, 3=Check Every Week | When enabled, the gateway will automatically request upgrades based on the configured time |
| `P286`    | `1`                                      | (Validate Firmware)                     | int |  |  |
| `P285`    | `1`                                      | (Always Check for New Firmware)         | int |  |  |
| `P8459`   | `22`                                     | (Upgrade Window Start Hour)             | int |  |  |
| `P193`    | `10080`                                  | (Auto Check Interval)                   | int |  |  |
| `P8458`   | `0`                                      | Randomized Automatic Upgrade            | boolean | 0=No, 1=Yes | Configures whether the device will upgrade automatically at a random time within the configured time interval. |
| `P238`    | `0`                                      | Firmware Upgrade and Provisioning       | enum | 0=Always Check for New Firmware at Boot up, 1=Check New Firmware only when F/... | Specifies how firmware upgrading and provisioning request to be sent. |
| `P8467`   | `0`                                      | Download and Process All Available Config Files | boolean | 0=No, 1=Yes | By default, the device will look for the first available configuration in the order of bootFileofDHCPOption67, cfgMAC.xml, cfgMAC, cfgMODEL.xml and cfg.xml for update. (Corresponding to bootfile, s... |
| `P8501`   | `cfg$mac.xml;cfg$mac;cfg$product.xml;cfg.xml` | Config Provision Order             | string |  | Device will provision the selected configuration files following the configured order. |

---

### Maintenance > Upgrade > Advanced (`/maintenance/upgrade/advancedSet`)

**Request (frame 577):**
```
P22030, P8601, P4428, P8463
```

**Response:**
| P-param  | Value  | Display Name                          | Type | Options/Range | Tooltip |
|----------|--------|---------------------------------------|------|------------|------------|
| `P22030` | `0`    | Advanced Settings                     | boolean | 0=No, 1=Yes | Configures to validate the hostname in the SSL certificate. |
| `P8601`  | `47`   | Configuration File Types Allowed      | enum | 47=All, 46=XML only | Allowed configuration file types, all or XML only. |
| `P4428`  | `0`    | Enable SIP NOTIFY Authentication      | boolean | 0=No, 1=Yes |  |
| `P8463`  | `0`    | Validate Server Certificates          | boolean | 0=No, 1=Yes |  |

---

### Maintenance > File Management > Call Records (`/maintenance/fileManage/call`)

**Request:**
```
P8534
```

CDR is retrieved via GET `/cgi-bin/api-get_cdr` and GET `/cgi-bin/api-preview_cdr`.

**Response:**
| P-param   | Value  | Display Name                          | Type | Options/Range | Tooltip |
|-----------|--------|---------------------------------------|------|------------|------------|
| `P8534`   | `1`    | CDR File Option                       | int |  |  |

CDR record schema:
```json
{
  "userId": "...",
  "toNumber": "...",
  "fromNumber": "...",
  "startTime": "...",
  "startTalkTime": "...",
  "endTime": "...",
  "duration": "...",
  "state": "...",
  "direction": "..."
}
```

---

### Maintenance > File Management > SIP Log (`/maintenance/fileManage/sip`)

**Request:**
```
P8535
```

SIP log existence is checked via GET `/cgi-bin/api-get_sip`.

**Response:**
| P-param   | Value  | Display Name                          | Type | Options/Range | Tooltip |
|-----------|--------|---------------------------------------|------|------------|------------|
| `P8535`   | `1`    | SIP Messages File Option              | int |  |  |

SIP log check response:
```json
{"results": [{"exist": "false"}]}
```

---

### Maintenance > Settings Management (`/maintenance/settingManage`)

**Request:**
```
P21929, P21930, P21931, P28118, P88
```

**Response:**
| P-param   | Value  | Display Name                          | Type | Options/Range | Tooltip |
|-----------|--------|---------------------------------------|------|------------|------------|
| `P21929`  | `0`    | Automatic restart                     | int |  | When enabled, the device will automatically restart at the configured time. |
| `P21930`  | `1`    | (Restart schedule - hour)             | int |  |  |
| `P21931`  | `1`    | (Restart schedule - day)              | int |  |  |
| `P28118`  | `1`    | (Settings management option)          | int |  |  |
| `P88`     | `0`    | Lock Keypad Update                    | boolean | 0=No, 1=Yes | configuration update via keypad is disabled if set to Yes |

---

### Maintenance > Voice Monitor (`/maintenance/voiceMonitor`)

**Request:**
```
P8489, P8490, P8491
```

**Response:**
| P-param   | Value  | Display Name                          | Type | Options/Range | Tooltip |
|-----------|--------|---------------------------------------|------|------------|------------|
| `P8489`   | `0`    | VQ RTCP-XR Session Report             | boolean | 0=No, 1=Yes | When enabled, phone will send a session quality report to the central report collector at the end of each call. |
| `P8490`   | `0`    | VQ RTCP-XR Interval Report            | boolean | 0=No, 1=Yes | Configures the interval (in seconds) of the device sending an interval quality report to the central report collector periodically throughout a call. |
| `P8491`   | `4`    | VQ RTCP-XR Interval Report Period     | enum | 1=5, 2=10, 3=15, 4=20 | Configures the interval (in seconds) of the phone sending an interval quality report to the central report collector periodically throughout a call. |

---

### Maintenance > Diagnostics > Syslog (`/maintenance/diagnostics/syslog`)

**Request:**
```
P207, P208, P8402, P8723, P1387
```

**Response:**
| P-param   | Value  | Display Name                          | Type | Options/Range | Tooltip |
|-----------|--------|---------------------------------------|------|------------|------------|
| `P207`    | `""`   | System Diagnosis (Syslog Server)      | string |  | Set the IP address or URL of the system log server |
| `P208`    | `1`    | Syslog Level                          | enum | 0=NONE, 5=EXTRA, 1=DEBUG, 2=INFO, 3=WARNING, 4=ERROR | Set the level of system log. By default, the device does not send any log information. |
| `P8402`   | `0`    | Syslog Protocol                       | enum | 0=UDP, 1=SSL/TLS | Allows sending syslog through secured TLS protocol to the syslog server<br/>Note: CA verification is required. |
| `P8723`   | `0`    | Syslog Header Format                  | enum | 0=Default, 1=RFC3164 Compliant |  |
| `P1387`   | `0`    | Send SIP Log                          | boolean | 0=No, 1=Yes | Configures whether the SIP logs will be included in the syslog messages. |

---

## Port 1 ↔ Port 2 P-Parameter Mapping

The two FXS ports share the same settings structure but use different P-parameter numbers. Key mappings:

| Setting                          | Port 1   | Port 2   |
|----------------------------------|----------|----------|
| Account Active                   | P271     | P401     |
| SIP Server                       | P47      | P747     |
| SIP User ID                      | P35      | P735     |
| Auth ID                          | P36      | P736     |
| Auth Password                    | P3       | P703     |
| SIP Registration                 | P31      | P731     |
| SIP Transport                    | P130     | P830     |
| Local SIP Port                   | P40      | P740     |
| RTP Port                         | P39      | P739     |
| Codec Choice 1                   | P850     | P860     |
| Codec Choice 2                   | P851     | P861     |
| Codec Choice 3                   | P852     | P862     |
| Voice Frames/TX                  | P37      | P737     |
| Analog Signal Line Configuration | P854     | P864     |
| Caller ID Scheme                 | P853     | P863     |
| DTMF Caller ID                   | P4661    | P4663    |
| Loop Current Disconnect          | P892     | P893     |
| Loop Current Disconnect Duration | P856     | P857     |
| Dial Plan                        | P4200    | P4201    |
| Off-hook Auto Dial               | P71      | P771     |
| Ring Timeout                     | P185     | P816     |
| No Answer Timeout                | P139     | P470     |
| Special Feature                  | P198     | P767     |
| Conference URI                   | P2318    | P2418    |
| Call Features Enable             | P191     | P751     |
| Call Features Reset              | P24199   | P24399   |
| Custom Ring Tone 1               | P870     | P880     |
| Custom Ring Tone 2               | P872     | P882     |
| Custom Ring Tone 3               | P874     | P884     |
| Ring Cadence 1                   | P4010    | P4030    |
| Ring Cadence 2                   | P4011    | P4031    |
| CW Tone Enable 1                | P29074   | P29174   |
| CW Tone Pattern 1               | P29080   | P29180   |
| Bellcore 3WC                     | P4830    | P4831    |
| DND                              | dnd_0    | dnd_1    |
| Hook Status                      | P4901    | P4902    |
| Reg Status                       | P4921    | P4922    |

---

## Web UI Page → URL Mapping Summary

| Page                                      | URL Path                                       |
|-------------------------------------------|-------------------------------------------------|
| Status > System Info                      | `/status/systemInfo`                            |
| Status > Network Status                   | `/status/netStatus`                             |
| Status > Port Status                      | `/status/portStatus`                            |
| Network Settings > Ethernet > Basic       | `/networkSetting/ethernet/basicSet`             |
| Network Settings > Advanced > Advanced    | `/networkSetting/advanced/advancedSet`          |
| Network Settings > Advanced > DNS Cache   | `/networkSetting/advanced/dnsCache`             |
| Network Settings > DDNS                   | `/networkSetting/DDNS`                          |
| Network Settings > OpenVPN               | `/networkSetting/openVpn`                       |
| System Settings > Basic                   | `/systemSetting/basic`                          |
| System Settings > Timezone & Language     | `/systemSetting/timezoneAndLang`                |
| System Settings > Tone                    | `/systemSetting/tone`                           |
| System Settings > Security > Remote       | `/systemSetting/security/remote`                |
| System Settings > Security > User Info    | `/systemSetting/security/userInfo`              |
| System Settings > Security > Certificate  | `/systemSetting/security/certificate`           |
| System Settings > Security > CA Cert      | `/systemSetting/security/cacert`                |
| System Settings > Management > TR-069     | `/systemSetting/manageSet/tr069`                |
| System Settings > Management > SNMP       | `/systemSetting/manageSet/snmp`                 |
| System Settings > Management > Interface  | `/systemSetting/manageSet/interfaceManage`      |
| System Settings > RADIUS                  | `/systemSetting/radius`                         |
| System Settings > E911/HELD               | `/systemSetting/e911held`                       |
| Port Settings > Port N > General          | `/portSetting/{n}/general`                      |
| Port Settings > Port N > SIP              | `/portSetting/{n}/sip`                          |
| Port Settings > Port N > Codec            | `/portSetting/{n}/codec`                        |
| Port Settings > Port N > Analog Line      | `/portSetting/{n}/analogline`                   |
| Port Settings > Port N > Call             | `/portSetting/{n}/call`                         |
| Port Settings > Port N > Advanced         | `/portSetting/{n}/advance`                      |
| Port Settings > Port N > Call Features    | `/portSetting/{n}/callfeature`                  |
| Port Settings > Port N > Tone             | `/portSetting/{n}/tone`                         |
| Maintenance > Firmware                    | `/maintenance/upgrade/firmware`                 |
| Maintenance > Config                      | `/maintenance/upgrade/config`                   |
| Maintenance > Deploy                      | `/maintenance/upgrade/deploy`                   |
| Maintenance > Advanced                    | `/maintenance/upgrade/advancedSet`              |
| Maintenance > File Manage > Call Records  | `/maintenance/fileManage/call`                  |
| Maintenance > File Manage > SIP Log       | `/maintenance/fileManage/sip`                   |
| Maintenance > Settings Management         | `/maintenance/settingManage`                    |
| Maintenance > Voice Monitor               | `/maintenance/voiceMonitor`                     |
| Maintenance > Diagnostics > Syslog        | `/maintenance/diagnostics/syslog`               |

---

## Codec Value Reference

From the config, codec numeric values used in P57-P62, P850-P852 etc.:

| Value | Codec          |
|-------|----------------|
| `0`   | G.711 u-law    |
| `2`   | G.726-32       |
| `4`   | G.723.1        |
| `8`   | G.711 a-law    |
| `9`   | G.722          |
| `18`  | G.729A/B       |
| `50`  | G.722.2 (AMR-WB)|
| `97`  | iLBC           |
| `98`  | Opus           |
| `100` | PCMU           |
| `101` | PCMA           |
| `102` | G.729          |

---

## Notes for MCP Server Implementation

1. **Authentication flow:** POST to `/cgi-bin/dologin` -> store the `session_token` from the JSON body **and** the `session_id` cookie from the `Set-Cookie` header -> include both in all subsequent requests. The cookie is essential; without it, all requests return "error" or "invalid session" even with a valid token.
2. **Cookie caveat:** The `session_id` cookie is set by an IP address, not a hostname. HTTP clients that enforce RFC 2965 cookie domain rules (e.g. Python `aiohttp.CookieJar`) will silently discard it. Use permissive/unsafe cookie handling when the device is accessed by IP.
3. **Session expiry:** Sessions time out after ~10-15 minutes of inactivity. Rather than polling keep-alive, it is simpler to detect errors and re-authenticate on demand.
4. **Reading settings:** Use `POST /cgi-bin/api.values.get` with `request=P1:P2:P3&session_token=<token>`
5. **Bulk config download:** GET `/cgi-bin/download_cfg` returns all 1798 P-values as text, GET `/cgi-bin/download_cfg_xml` for XML format
6. **All values are strings** in the JSON responses, even numeric ones
7. **Virtual fields** (non-P-prefixed like `mac_display`, `serial_number`, `cpu_load`, `net_cable_status`, etc.) are computed/status fields that can also be requested via `api.values.get`
8. **Product info:** POST `/cgi-bin/api-get_system_base_info` returns product model and vendor name
9. **CDR/SIP logs:** Use dedicated endpoints `/cgi-bin/api-get_cdr`, `/cgi-bin/api-preview_cdr`, and `/cgi-bin/api-get_sip` for call records and SIP log data
