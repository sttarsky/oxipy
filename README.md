# oxipy

`oxipy` is a Python client for the [Oxidized](https://github.com/ytti/oxidized) API.
It fetches device configurations from Oxidized and parses them into structured
Pydantic models using bundled TTP templates.

Oxidized remains responsible for collecting and storing configuration backups.
`oxipy` focuses on consuming those backups from Python code and exposing common
configuration sections such as system data, interfaces, and VLANs.

## Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
  - [OxiAPI](#oxiapi)
  - [NodeView](#nodeview)
  - [NodeConfig](#nodeconfig)
  - [ModelView](#modelview)
- [Supported Devices](#supported-devices)
- [Additional Documentation](#additional-documentation)

## Installation

The package is distributed through a private Gitea Package Registry and from the
source repository. It is not published to PyPI.

**Requirements:** Python 3.10+

### From Gitea Package Registry

Install the package by pointing `pip` to the private registry:

```bash
pip install oxipy \
  --index-url https://gitea.imbastark.ru/api/packages/Netbox/pypi/simple/
```

You can also configure the registry permanently in `pip.conf` or `pip.ini`:

```ini
# ~/.config/pip/pip.conf  (Linux/macOS)
# %APPDATA%\pip\pip.ini   (Windows)

[global]
extra-index-url = https://gitea.imbastark.ru/api/packages/Netbox/pypi/simple/
```

After that, install normally:

```bash
pip install oxipy
```

If the registry requires authentication, pass a token in the index URL:

```bash
pip install oxipy \
  --index-url https://__token__:<your_token>@gitea.imbastark.ru/api/packages/Netbox/pypi/simple/
```

### From Gitea Source

Install directly from the repository:

```bash
pip install git+https://gitea.imbastark.ru/Netbox/oxipy.git
```

Install a specific tag or branch:

```bash
pip install git+https://gitea.imbastark.ru/Netbox/oxipy.git@v0.1.0
pip install git+https://gitea.imbastark.ru/Netbox/oxipy.git@dev
```

For local development:

```bash
git clone https://gitea.imbastark.ru/Netbox/oxipy
cd oxipy
pip install -e .
```

## Quick Start

```python
from oxi import OxiAPI

api = OxiAPI(url="https://oxi.example.com", verify=False)

node = api.node("Router_HOME")

print(node.ip)
print(node.model)
print(node.full_name)

print(node.config.system.model)
print(node.config.interfaces.dump_json())
print(node.config.vlans.dump_json())
```

Example output:

```text
192.168.1.1
keenetic
router/HQ
Sprinter (KN-3710)
[
  {"interface": "Bridge1", "ip_address": "192.168.1.1", "mask": 24, "description": "Guest network"},
  {"interface": "Bridge0", "ip_address": "172.16.1.1", "mask": 24, "description": "Home network"}
]
[
  {"vlan_id": 1, "description": "Home VLAN"},
  {"vlan_id": 2, "description": "Ethernet uplink"},
  {"vlan_id": 3, "description": "Home network"}
]
```

## API Reference

### OxiAPI

`OxiAPI` is the entry point. It manages the HTTP session and provides access to
Oxidized nodes.

```python
OxiAPI(
    url: str,
    username: str | None = None,
    password: str | None = None,
    verify: bool = True,
)
```

| Parameter | Type | Description |
| --- | --- | --- |
| `url` | `str` | Base URL of the Oxidized API, for example `https://oxi.example.com`. |
| `username` | `str | None` | Optional username for HTTP basic authentication. |
| `password` | `str | None` | Optional password for HTTP basic authentication. |
| `verify` | `bool` | Whether to verify TLS certificates. Defaults to `True`. |

Example:

```python
# Without authentication
api = OxiAPI(url="https://oxi.example.com")

# With HTTP basic authentication
api = OxiAPI(
    url="https://oxi.example.com",
    username="admin",
    password="secret",
)

# As a context manager. The HTTP session is closed automatically.
with OxiAPI(url="https://oxi.example.com") as api:
    node = api.node("HQ")
    print(node.ip)
```

#### `api.node(name)`

Returns a `NodeView` for the requested Oxidized node.

```python
node = api.node("HQ")
```

### NodeView

`NodeView` represents one network device. It contains metadata returned by
Oxidized and lazy access to the fetched configuration.

| Property | Type | Description |
| --- | --- | --- |
| `ip` | `str` | Node IP address. |
| `full_name` | `str` | Full node name in Oxidized. |
| `group` | `str` | Oxidized group the node belongs to. |
| `model` | `str` | Device model key used to select a parser. |
| `config` | `NodeConfig` | Device configuration, fetched and parsed on first access. |

Example:

```python
node = api.node("HQ")

print(node.ip)
print(node.group)
print(node.model)
```

### NodeConfig

`NodeConfig` fetches and parses a device configuration. The parser is selected
from the device registry by the node `model` value returned by Oxidized.

Configuration sections are exposed through properties that return `ModelView`
objects.

| Property | Returns | Description |
| --- | --- | --- |
| `system` | `ModelView[System]` | System information. |
| `interfaces` | `ModelView[list[Interfaces]]` | Parsed interface list. |
| `vlans` | `ModelView[list[Vlans]]` | Parsed VLAN list, if the template provides VLAN data. |
| `text` | `str` | Raw configuration text fetched from Oxidized. |

Example:

```python
cfg = node.config

print(cfg.system.model)
print(cfg.system.serial_number)
print(cfg.system.version)

for iface in cfg.interfaces:
    print(iface.name, iface.ip_address, iface.mask)

first_iface = cfg.interfaces[0]
print(first_iface.name)
print(len(cfg.interfaces))

print(cfg.interfaces.dump_json())
print(cfg.vlans.dump_json())
print(cfg.system.dump_json())

print(cfg.text)
```

`NodeConfig` also provides `dump()` and `dump_json()` methods for the whole
parsed device object.

### ModelView

`ModelView` wraps either a single Pydantic model or a list of Pydantic models.
It provides serialization, iteration for list sections, and transparent access
to model attributes.

| Method / operation | Applies to | Description |
| --- | --- | --- |
| `.dump()` | single model and list | Returns a Python `dict` or `list` using aliases. |
| `.dump_json()` | single model and list | Returns a JSON string using aliases. |
| `.<attr>` | single model and list | Proxies attribute access to the wrapped model. |
| `iter(view)` | list only | Iterates over wrapped models. |
| `len(view)` | list only | Returns the number of wrapped models. |
| `view[i]` | list only | Returns an item or slice. |

`__iter__`, `__len__`, and `__getitem__` are available only for list-backed
sections such as `interfaces` and `vlans`. Calling them on `system` raises
`TypeError`.

Examples:

```python
system = node.config.system
print(system.dump_json())
print(system.model)
print(system.serial_number)

interfaces = node.config.interfaces

for iface in interfaces:
    print(iface.name, iface.ip_address)

print(len(interfaces))
print(interfaces[0])
print(interfaces[:3])
print(interfaces.dump())
```

## Supported Devices

Registry keys are compared with the Oxidized node `model` value
case-insensitively.

| Device | Registry keys |
| --- | --- |
| Keenetic | `ndms`, `keenetic`, `keeneticos` |
| MikroTik | `routeros`, `ros`, `mikrotik` |
| Qtech | `qtech` |
| Huawei | `huawei`, `vrp` |
| Eltex | `eltex` |
| H3C | `h3c` |
| Quasar | `qos`, `quasar` |

You can add support for another device family by creating a new device model
and TTP template. See [Extending Device Models](docs/extending-models.md).

## Additional Documentation

- [Writing TTP Templates](docs/templates.md)
- [Extending Device Models](docs/extending-models.md)
