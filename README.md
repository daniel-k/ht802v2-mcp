# HT802 V2 MCP Server

MCP server for reading (and eventually writing) settings on the Grandstream HT802 V2 ATA.

## Project Status

**Phase: API research and documentation** — no code yet.

The device's web UI has been reverse-engineered from network captures. All HTTP API
endpoints, their request/response schemas, and the mapping of internal P-parameter
codes to human-readable UI labels have been documented.

## Device Background

The HT802 V2 is a 2-port FXS analog telephone adapter. Its web UI is a Vue.js SPA
that communicates with the device over a JSON HTTP API. All device configuration is
stored as numbered "P-parameters" (e.g. `P47` = Primary SIP Server, `P35` = SIP User
ID). The web UI maps these codes to display names via a locale system (`lan1234` keys).

## How the API Works

### Authentication

```
POST /cgi-bin/dologin
Body: username=admin&P2=<base64-encoded-password>
```

Returns a `session_token` (MD5 hex string) that must be included in all subsequent
requests. Three roles exist: `admin`, `user`, `viewer`.

### Reading Settings

The primary endpoint is:

```
POST /cgi-bin/api.values.get
Content-Type: application/x-www-form-urlencoded
Body: request=P47%3AP35%3AP40&session_token=<token>
```

The `request` field is a colon-separated (`:`, URL-encoded as `%3A`) list of
P-parameter names. The response is JSON with all values as strings:

```json
{"response": "success", "body": {"P47": "192.168.1.100", "P35": "15551234567", "P40": "5060"}}
```

You can also request virtual/computed fields like `mac_display`, `serial_number`,
`cpu_load`, `net_cable_status`, etc. through the same endpoint.

### Bulk Config Download

- `GET /cgi-bin/download_cfg?session_token=<token>` — all 1798 P-values as `P123=value` text
- `GET /cgi-bin/download_cfg_xml?session_token=<token>` — same as XML provisioning format

### Session Keep-Alive

The UI sends a keep-alive every ~10 seconds:

```
POST /cgi-bin/api-phone_operation
Body: arg=&cmd=extend&session_token=<token>
```

Session validity can be checked via `GET /cgi-bin/api-get_sessioninfo`.

### Other Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/cgi-bin/api-get_time` | GET | Device clock |
| `/cgi-bin/api-get_system_info` | GET | Process info, provision status |
| `/cgi-bin/api-get_system_base_info` | POST | Product/vendor (pre-login) |
| `/cgi-bin/api-get_apply_status` | POST | Pending reboot check |
| `/cgi-bin/api-get_values_rule` | GET | Factory defaults for all P-params |
| `/cgi-bin/api-get_device_password_rules` | GET | Password policy |
| `/cgi-bin/api-get_cdr` | GET | Call detail records |
| `/cgi-bin/api-preview_cdr` | GET | CDR download |
| `/cgi-bin/api-get_sip` | GET | SIP log existence check |

Full request/response schemas for every endpoint are in [`api-docs.md`](api-docs.md).

## P-Parameter Architecture

Every setting has a numeric P-parameter code. The two FXS ports share the same
setting structure but use different P-numbers. Some key mappings:

| Setting | Port 1 | Port 2 |
|---------|--------|--------|
| Account Active | P271 | P401 |
| SIP Server | P47 | P747 |
| SIP User ID | P35 | P735 |
| Auth Password | P3 | P703 |
| Local SIP Port | P40 | P740 |
| Local RTP Port | P39 | P739 |
| Codec Choice 1 | P850 | P860 |

The full config has 1798 P-values. The web UI groups them into pages that each
request a specific subset via `api.values.get`. All 39 UI pages and their exact
P-parameter lists are documented in `api-docs.md`.

## Web UI Page Map

| Section | Pages |
|---------|-------|
| Status | System Info, Network Status, Port Status |
| Network Settings | Ethernet Basic, Advanced, DNS Cache, DDNS, OpenVPN |
| System Settings | Basic, Timezone, Tone, Security (Remote/UserInfo/Cert/CA), Management (TR-069/SNMP/Interface), RADIUS, E911/HELD |
| Port Settings (x2) | General, SIP, Codec, Analog Line, Call, Advanced, Call Features, Tone |
| Maintenance | Firmware, Config, Deploy, Advanced/Syslog, Call Records, SIP Log, Settings Management, Voice Monitor |

## Repository Structure

```
api-docs.md              Full API + per-page field reference with display names
README.md                This file
web_ui.pcapng.gz         First capture session (status, network, system, port 1, maintenance)
web_ui_2.pcapng.gz       Second capture session (locale data, new pages, port 2 remaining)
web_ui.pcapng            Decompressed first capture
web_ui_2.pcapng          Decompressed second capture
web_ui_3.pcapng          Third capture (Port 2 callfeature/tone, reboot)
tmp/                     Extracted artifacts from captures
  locale_en.txt          1833 English UI strings (lan1234=Display Name)
  p_to_lang.txt          1076 P-param to locale key mappings (P123=lan456)
  p_display_names.txt    Joined: P-param + locale key + English display name
  field_defs_app.txt     850 form field definitions from JS (lang/element/p-value triples)
  config_full.txt        Full device config dump (1798 P-values)
  config.xml             Same config in XML provisioning format
  networksetting.js      NetworkSetting Vue component source
  ht802_stream*.bin      Raw TCP streams from capture 2 (JS/CSS bundles)
  locale_raw.txt         All locale strings including CN/ES (7139 entries)
  locale_all.txt         Intermediate extraction artifact
```

## Research Notes

### How the reverse engineering was done

1. Two browser sessions were captured with the device web UI using pcapng
2. HTTP request/response pairs were extracted with tshark
3. `api.values.get` POST bodies were decoded to get the P-parameter lists per page
4. Referer headers revealed which UI page triggered each API call
5. The app.js bundle (~694KB) was extracted from TCP stream reassembly and parsed
   for locale strings (`lan1234:"English Text"`) and field definitions
   (`lang:"lan1234",el:"select",p:"P567"`)
6. Display names were joined: P-param -> locale key -> English string

### Gotchas discovered

- **All values are strings** in JSON responses, even booleans and numbers
- **Password field** (P2 in login) is base64-encoded, not the raw password
- **Virtual fields** like `mac_display`, `serial_number`, `cpu_load` are not
  P-parameters but can be requested through the same `api.values.get` endpoint
- **Session token** is an MD5 hex string, valid until timeout (~15 min idle)
- **The UI polls** `api-get_sessioninfo` every 10s and sends `api-phone_operation`
  with `cmd=extend` to keep the session alive
- **Port conflict checking**: several pages (Security > Remote, TR-069, SNMP) load
  a set of port P-values (`P901, P4518, P21903, P27010, P27006, P28128, P150-P157`)
  to validate that configured ports don't collide
- **DNS cache table** uses a strided P-parameter scheme: base + (index * 20) + suffix,
  where suffix encodes the field type (00=domain, 01=TTL, 02=type, etc.)
- **api-get_values_rule** returns factory defaults with a `{"def": "value"}` wrapper
  per parameter, unlike `api.values.get` which returns bare values
- **Two response formats** exist: some endpoints use `{"response":"success","body":{...}}`
  while others use `{"results":[...]}`
- **Locale keys are not quoted** as JSON keys in the JS bundle — they appear as
  `lan1234:"text"` not `"lan1234":"text"`, which affects extraction regex
- The same P-parameter can appear in multiple locale mappings (e.g. P35 maps to
  both `lan1027` "SIP User ID" on the status page and `lan5015` "SIP User ID" on
  the settings page) — context determines which label is shown

### Coverage gaps

The following are known but not yet captured/documented:

- **Writing settings** (`api.values.set` or similar) — not attempted yet
- **File upload endpoints** (firmware, config, certificates) — not captured
- **Factory reset** — not captured (reboot is documented as `POST /cgi-bin/rs`)
- Some P-parameters in `config_full.txt` (1798 total) don't appear in any UI page
  and may be internal/deprecated or only accessible via provisioning

Note: The JS bundles contain components for LAN Set and Port Forwarding pages, but
these do not exist on the HT802V2 — they are shared code from other Grandstream
models (e.g. HT81x with router mode). Navigating to those URLs redirects to
System Info.
