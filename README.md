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
- [Error Handling](#error-handling)
- [Supported Devices](#supported-devices)
- [Additional Documentation](#additional-documentation)

## Installation

The package is distributed from the source repository. It is not published to
PyPI yet.

**Requirements:** Python 3.10+

### From GitHub Source

Install directly from the repository:

```bash
pip install git+https://github.com/sttarsky/oxipy.git
```

Install a specific tag or branch:

```bash
pip install git+https://github.com/sttarsky/oxipy.git
pip install git+https://github.com/sttarsky/oxipy.git@dev
```

For local development:

```bash
git clone https://github.com/sttarsky/oxipy
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
print(node.config.interfaces.dump())
print(node.config.vlans.dump_json())
```

Example output:

```text
192.168.1.1
keenetic
router/HQ
Sprinter (KN-3710)
[
  {"interface": "Bridge1", "ip_address": "192.168.1.1", "mask": 24, "description": "Guest network", "shutdown": false},
  {"interface": "Bridge0", "ip_address": "172.16.1.1", "mask": 24, "description": "Home network", "shutdown": false}
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
| `username` | `str` | `None` | Optional username for HTTP basic authentication. |
| `password` | `str` | `None` | Optional password for HTTP basic authentication. |
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

#### `api.add_alias(alias, model)`

Maps extra model name(s) to an already registered device parser. Use it when
your Oxidized installation reports a custom `model` value for a device that a
built-in parser already handles.

```python
api.add_alias("my-router-os", "mikrotik")
api.add_alias(["vrp-custom", "hw-campus"], "huawei")
```

- `alias` is a single name or a list of names as they appear in Oxidized.
- `model` is an existing registry key (case-insensitive), see
  [Supported Devices](#supported-devices).
- Raises `UnknownModelError` if `model` is not registered.

The parser registry is process-wide: aliases added through one `OxiAPI`
instance are visible to all instances. The method is a `staticmethod`, so it
can also be called as `OxiAPI.add_alias(...)` before creating a connection.

#### `api.reload()`

Asks Oxidized to reload its node list (`GET /reload`). Returns the HTTP status
code and raises `OxiConnectionError` on failure.

```python
api.reload()
```

### NodeView

`NodeView` represents one network device. It contains metadata returned by
Oxidized and lazy access to the fetched configuration.

| Property | Type | Description |
| --- | --- | --- |
| `name` | `str` | Short node name. |
| `ip` | `str` | Node IP address. |
| `full_name` | `str` | Full node name in Oxidized. |
| `group` | `str` | Oxidized group the node belongs to. |
| `model` | `str` | Device model key used to select a parser. |
| `last_status` | `str` | Status of the last Oxidized backup job. |
| `last_check` | `str` | Start time of the last Oxidized backup job. |
| `config` | `NodeConfig` | Device configuration, fetched and parsed on first access. |

The `config` object is cached on the node: repeated `node.config` accesses
reuse the same fetched and parsed configuration and do not hit the network
again.

Example:

```python
node = api.node("HQ")

print(node.ip)
print(node.group)
print(node.model)
print(node.last_status)
```

#### `node.refresh()`

Asks Oxidized to schedule the node for the next backup run
(`GET /node/next/<name>`). Returns `"OK"` on success and raises `ValueError`
on failure.

### NodeConfig

`NodeConfig` fetches and parses a device configuration. The parser is selected
from the device registry by the node `model` value returned by Oxidized.

Configuration sections are exposed through properties that return `ModelView`
objects.

| Property | Returns | Description |
| --- | --- | --- |
| `system` | `ModelView[System]` | System information: `model`, `serial_number`, `version`. |
| `interfaces` | `ModelView[list[Interfaces]]` | Parsed interfaces: `name`, `ip_address`, `mask`, `description`, `shutdown`. |
| `vlans` | `ModelView[list[Vlans]]` | Parsed VLANs (`vlan_id`, `name`), if the template provides VLAN data. |
| `text` | `str` | Raw configuration text fetched from Oxidized. |

Example:

```python
cfg = node.config

print(cfg.system.model)
print(cfg.system.serial_number)
print(cfg.system.version)

for iface in cfg.interfaces:
    print(iface.name, iface.ip_address, iface.mask, iface.shutdown)

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
`OxiConnectionError`.

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

## Error Handling

All exceptions raised by `oxipy` derive from a single base class, `OxiError`.
Catch `OxiError` to handle any library-specific failure in one place, or catch a
specific subclass when you need to react differently. Every exception is
importable from the top-level `oxi` package.

```text
OxiError                     # base class for every oxipy error
├── OxiConnectionError       # real transport/HTTP failure (has .status_code)
├── NodeNotFoundError        # the node does not exist in Oxidized
├── ConfigNotAvailableError  # the node exists, but there is no config to parse
├── ConfigParseError         # a config was fetched but could not be parsed
├── UnknownModelError        # the device model is not in the parser registry
└── TemplateError            # the TTP template is missing or invalid
```

| Exception | Raised when | Typical cause |
| --- | --- | --- |
| `OxiConnectionError` | A request fails with a genuine server/transport error. | 5xx, `401/403`, timeouts. `.status_code` holds the HTTP status. |
| `NodeNotFoundError` | The requested node does not exist. | `GET /node/show/<name>` returns a real `404`, or Oxidized's `500` page titled `Oxidized::NodeNotFound`. |
| `ConfigNotAvailableError` | The node exists, but Oxidized returned no configuration. | `GET /node/fetch/<name>` responds `200` with the body `node not found` (no backup yet). |
| `ConfigParseError` | A config was fetched but could not be turned into a model. | The TTP template produced no required sections, or parsed data failed Pydantic validation (original error kept in `__cause__`). |
| `UnknownModelError` | The device model has no registered parser. | The node `model` value (or an `add_alias` target) is not in the registry. |
| `TemplateError` | The TTP template cannot be loaded or is structurally invalid. | The template file is missing, or it does not declare the required groups. |

### Why "not found" is split into three exceptions

Oxidized signals a missing node inconsistently, so `oxipy` normalizes it into
distinct, meaningful exceptions:

- The node is not registered at all -> `NodeNotFoundError`.
- The node is registered but has no stored backup yet -> `ConfigNotAvailableError`.
- The backup exists but the parser cannot process it -> `ConfigParseError`.

This lets you tell "no such device" apart from "device exists but has no data"
without inspecting HTTP status codes.

### Example

```python
from oxi import (
    OxiAPI,
    OxiError,
    NodeNotFoundError,
    ConfigNotAvailableError,
    ConfigParseError,
    OxiConnectionError,
)

api = OxiAPI(url="https://oxi.example.com")

try:
    config = api.node("HQ").config
    print(config.system.model)
except NodeNotFoundError:
    print("No such node in Oxidized")
except ConfigNotAvailableError:
    print("Node exists, but has no backup yet")
except ConfigParseError as exc:
    # The underlying parser/validation error is preserved on __cause__.
    print(f"Could not parse config: {exc.__cause__}")
except OxiConnectionError as exc:
    print(f"Oxidized request failed (HTTP {exc.status_code})")
except OxiError:
    print("Some other oxipy error")
```

`OxiConnectionError` is the only exception that carries an HTTP `status_code`;
the others describe domain conditions and do not expose one.

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

If your Oxidized installation uses a different `model` value for one of these
devices, map it with [`api.add_alias`](#apiadd_aliasalias-model):

```python
api.add_alias("my-router-os", "mikrotik")
```

You can add support for another device family by creating a new device model
and TTP template. See [Extending Device Models](docs/extending-models.md).

## Additional Documentation

- [Writing TTP Templates](docs/templates.md)
- [Extending Device Models](docs/extending-models.md)
