# Extending Device Models

`oxipy` parses an Oxidized configuration in two stages. A TTP template first
extracts raw dictionaries from the text, then a device model normalizes those
dictionaries before Pydantic validates them against the public contract.

Device models extend `BaseDevice`. Override `system()`, `interfaces()`, or
`vlans()` when the raw TTP result needs vendor-specific cleanup.

## Contents

- [Data Flow](#data-flow)
- [Registering a Device](#registering-a-device)
- [Method Overrides](#method-overrides)
  - [interfaces()](#interfaces)
  - [vlans()](#vlans)
  - [system()](#system)
- [Complete Example](#complete-example)
- [Expected Contract](#expected-contract)

## Data Flow

```text
configuration text
        |
        v
   TTP template (.ttp)
        |
        v
   self.raw: dict
        |
        +--> system()     -> dict
        +--> interfaces() -> list[dict]
        +--> vlans()      -> list[dict]
        |
        v
   Pydantic validation
        |
        v
   Device(system, interfaces, vlans)
```

The extension methods are intentionally small. The base implementation returns
data directly from `self.raw`:

```python
def interfaces(self) -> list[dict]:
    return self.raw.get("interfaces", [])

def vlans(self) -> list[dict]:
    return self.raw.get("vlans", [])

def system(self) -> dict:
    return self.raw.get("system", None)
```

## Registering a Device

To add support for a new vendor:

1. Create a Python file in `oxi/interfaces/models/`, for example `cisco.py`.
2. Create a template in `oxi/interfaces/models/templates/`, for example
   `cisco.ttp`.
3. Subclass `BaseDevice` and register it with `@register_parser`.

```python
from oxi.interfaces import register_parser
from oxi.interfaces.base import BaseDevice


@register_parser(["ios", "cisco", "cisco_ios"])
class CiscoIOS(BaseDevice):
    template = "cisco.ttp"
```

`@register_parser` accepts a string or a list of strings. These values are the
registry keys used to match the Oxidized node `model` field. Matching is
case-insensitive.

Model modules are imported automatically through `pkgutil` when
`oxi.interfaces` is loaded, so you do not need to import your model class
manually.

## Method Overrides

### interfaces()

Override `interfaces()` when you need to:

- Convert dotted decimal netmasks to prefix lengths.
- Decode escaped descriptions.
- Rename keys that do not match the contract.
- Filter service-only interfaces.

Example: convert a netmask to a prefix length.

```python
from ipaddress import ip_interface
from oxi.interfaces import register_parser
from oxi.interfaces.base import BaseDevice


@register_parser(["myvendor"])
class MyVendor(BaseDevice):
    template = "myvendor.ttp"

    def interfaces(self) -> list[dict]:
        result = []
        for item in self.raw.get("interfaces", []):
            if item.get("ip_address") and item.get("netmask"):
                iface = ip_interface(f"{item['ip_address']}/{item['netmask']}")
                item["mask"] = iface.network.prefixlen
                item.pop("netmask", None)
            result.append(item)
        return result
```

Example: filter management interfaces.

```python
def interfaces(self) -> list[dict]:
    return [
        item for item in self.raw.get("interfaces", [])
        if not item.get("interface", "").startswith("Mgmt")
    ]
```

Example: decode escaped UTF-8 descriptions.

```python
def _decode_utf(self, text: str) -> str:
    if "\\x" in text:
        return (
            text.strip('"')
            .encode("utf-8")
            .decode("unicode_escape")
            .encode("latin1")
            .decode("utf-8")
        )
    return text


def interfaces(self) -> list[dict]:
    interfaces = self.raw.get("interfaces", [])
    for item in interfaces:
        if item.get("description"):
            item["description"] = self._decode_utf(item["description"])
    return interfaces
```

### vlans()

Override `vlans()` to normalize VLAN IDs, expand compressed ranges, decode
names, or merge details from multiple template groups.

Example: add a generated VLAN name.

```python
def vlans(self) -> list[dict]:
    result = []
    for item in self.raw.get("vlans", []):
        item["description"] = f"VLAN_{item.get('vlan_id', '?')}"
        result.append(item)
    return result
```

Example: merge data from another raw group.

```python
def vlans(self) -> list[dict]:
    vlans = {item["vlan_id"]: item for item in self.raw.get("vlans", [])}
    for extra in self.raw.get("vlan_details", []):
        vlan_id = extra.get("vlan_id")
        if vlan_id in vlans:
            vlans[vlan_id].update(extra)
    return list(vlans.values())
```

Example: expand a comma-separated VLAN range.

```python
def _expand_vlan_range(value: str) -> list[str]:
    result = []
    for part in value.split(","):
        if "-" not in part:
            result.append(part.strip())
            continue
        start, end = (int(item) for item in part.split("-", 1))
        result.extend(str(vlan_id) for vlan_id in range(start, end + 1))
    return result
```

### system()

Override `system()` when the system section needs computed fields or data from
another raw group.

Example: assemble a serial number from two fields.

```python
def system(self) -> dict:
    raw_system = self.raw.get("system", {})
    part1 = raw_system.get("serial_part1", "")
    part2 = raw_system.get("serial_part2", "")
    raw_system["serial_number"] = f"{part1}-{part2}"
    return raw_system
```

Example: normalize a version string.

```python
def system(self) -> dict:
    raw_system = self.raw.get("system", {})
    version = raw_system.get("version", "")
    raw_system["version"] = version.split()[0] if version else version
    return raw_system
```

## Complete Example

Assume a Cisco IOS-like device where:

- IP address and netmask are separated by a space.
- Interface descriptions can contain several words.
- System fields are present in separate lines.

Template: `oxi/interfaces/models/templates/cisco.ttp`

```xml
<vars>
default_system = {
    "model": "",
    "serial_number": "",
    "version": ""
}
</vars>

<group name="system" default="default_system">
Cisco IOS Software, {{ ignore }} Version {{ version }},{{ ignore('.*') }}
Model Number         : {{ model }}
System serial number : {{ serial_number }}
</group>

<group name="interfaces">
interface {{ interface | _start_ }}
 description {{ description | ORPHRASE }}
 ip address {{ ip_address }} {{ netmask }}
</group>

<group name="vlans">
vlan {{ vlan_id | _start_ }}
 name {{ name | ORPHRASE }}
</group>
```

Device model: `oxi/interfaces/models/cisco.py`

```python
from ipaddress import ip_interface
from oxi.interfaces import register_parser
from oxi.interfaces.base import BaseDevice


@register_parser(["ios", "cisco", "cisco_ios"])
class CiscoIOS(BaseDevice):
    template = "cisco.ttp"

    def interfaces(self) -> list[dict]:
        result = []
        for item in self.raw.get("interfaces", []):
            if item.get("ip_address") and item.get("netmask"):
                iface = ip_interface(f"{item['ip_address']}/{item['netmask']}")
                item["mask"] = iface.network.prefixlen
                item.pop("netmask", None)
            if item.get("interface", "").startswith("Mgmt"):
                continue
            result.append(item)
        return result

    def system(self) -> dict:
        raw_system = self.raw.get("system", {})
        if raw_system.get("model"):
            raw_system["model"] = raw_system["model"].strip()
        return raw_system
```

## Expected Contract

Methods must return structures accepted by `oxi.interfaces.contract`.

### `system() -> dict`

```python
{
    "model": "RB951Ui-2nD",
    "serial_number": "B88C0B31117B",
    "version": "7.12.1",
}
```

### `interfaces() -> list[dict]`

```python
[
    {
        "interface": "ether1",
        "ip_address": "192.168.1.1",
        "mask": 24,
        "description": "LAN",
    },
]
```

### `vlans() -> list[dict]`

```python
[
    {
        "vlan_id": 10,
        "description": "MGMT",
    },
]
```

The Pydantic models use `populate_by_name=True` for aliased models, so both
field names and aliases are accepted where aliases exist.
