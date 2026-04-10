# HT802 V2 MCP Server

MCP server for managing Grandstream HT802 V2 analog telephone adapters.

## Usage

### With Claude Code

Add to your `.claude/settings.json`:

```json
{
  "mcpServers": {
    "ht802": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/ht802v2-mcp", "ht802v2-mcp"],
      "env": {
        "HT802_HOST": "192.168.1.1",
        "HT802_PASSWORD": "your-password"
      }
    }
  }
}
```

### Standalone

```sh
HT802_HOST=192.168.1.1 HT802_PASSWORD=secret uv run ht802v2-mcp
```

### PEX executable

```sh
tox -e pex
HT802_HOST=192.168.1.1 HT802_PASSWORD=secret ./dist/ht802v2-mcp.pex
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HT802_HOST` | `192.168.1.1` | Device IP address |
| `HT802_PORT` | `80` | HTTP port |
| `HT802_USERNAME` | `admin` | Login username (`admin`, `user`, or `viewer`) |
| `HT802_PASSWORD` | *(empty)* | Login password |
| `HT802_USE_SSL` | `false` | Use HTTPS |
| `HT802_VERIFY_SSL` | `false` | Verify TLS certificate |

## Available Tools

| Tool | Description |
|------|-------------|
| `get_system_info` | Model, serial, MAC, firmware versions, uptime, CPU load |
| `get_base_info` | Product model and vendor name |
| `get_network_status` | IP addresses, cable status, NAT, PPPoE, VPN, certificate |
| `get_port_status` | FXS port 1 & 2: hook state, SIP user, registration |
| `get_device_time` | Current device clock |
| `get_apply_status` | Whether a reboot/apply is pending |
| `get_system_process_info` | ATA process memory, provisioning status, core dump |
| `get_values` | Read arbitrary P-parameters by name |
| `get_session_info` | Session timeout/expiry status |
| `extend_session` | Send keep-alive to extend the session |
| `reboot` | Reboot the device (~60s downtime) |

## Device API Overview

The HT802 V2 web UI is a Vue.js SPA backed by a JSON HTTP API under `/cgi-bin/`.

### Authentication

Login via `POST /cgi-bin/dologin` with the password base64-encoded in the `P2` field.
Returns a session token (MD5 hex string) included in all subsequent requests.
Sessions time out after ~15 minutes of inactivity; the UI polls keep-alive every ~10s.

### P-Parameters

All device configuration is stored as numbered P-parameters (e.g. `P47` = Primary SIP
Server, `P35` = SIP User ID). The two FXS ports share the same settings structure but
use different P-numbers:

| Setting | Port 1 | Port 2 |
|---------|--------|--------|
| Account Active | P271 | P401 |
| SIP Server | P47 | P747 |
| SIP User ID | P35 | P735 |
| Auth Password | P3 | P703 |
| Local SIP Port | P40 | P740 |

The primary read endpoint is `POST /cgi-bin/api.values.get` with a colon-separated
list of parameter names. All values are returned as strings. Virtual fields like
`mac_display`, `serial_number`, and `cpu_load` use the same endpoint.

Full endpoint and field documentation is in [`api-docs.md`](api-docs.md).

## Development

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```sh
uv sync                  # install dependencies
tox -e lint              # run ruff linter
tox -e format            # check formatting
tox -e pex               # build single-file executable
```

## License

MIT
