# Writing TTP Templates

`oxipy` uses [TTP (Template Text Parser)](https://ttp.readthedocs.io/) to turn
network device configurations fetched from Oxidized into structured data.
Templates are stored in `oxi/interfaces/models/templates/`.

## Contents

- [Template Structure](#template-structure)
- [Required Groups](#required-groups)
- [The system Group](#the-system-group)
- [The interfaces Group](#the-interfaces-group)
- [The vlans Group](#the-vlans-group)
- [Useful TTP Features](#useful-ttp-features)
- [Default Variables](#default-variables)
- [Full Example](#full-example)
- [Validation](#validation)

## Template Structure

Each template is a `.ttp` file with a small set of conventional blocks:

```xml
<doc>
    Optional template documentation.
</doc>

<vars>
    <!-- Default values for groups. -->
</vars>

<group name="system">
    <!-- Rules for system information. -->
</group>

<group name="interfaces">
    <!-- Rules for interfaces. -->
</group>

<group name="vlans">
    <!-- Optional rules for VLANs. -->
</group>
```

Use `oxi/interfaces/models/templates/_template.ttp` as the starting point for a
new parser.

## Required Groups

The framework requires two groups in every template:

| Group | Required | Description |
| --- | --- | --- |
| `system` | Yes | Device system information. |
| `interfaces` | Yes | Interface configuration. |
| `vlans` | No | VLAN configuration. |

If a required group is missing from the template or from the TTP result,
`BaseDevice` raises `ValueError`.

If a template declares an optional `vlans` group, `oxipy` expects TTP to return
that group. Omit the group completely for devices where VLAN parsing is not
implemented.

## The system Group

The `system` group must return one dictionary with these fields:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `model` | `str` | Yes | Device model. |
| `serial_number` | `str` | Yes | Device serial number. |
| `version` | `str` | Yes | Firmware, software, or build version chosen by the parser. |

Example for MikroTik:

```text
# version: 7.12.1 (stable)
# model = RB951Ui-2nD
# serial number = B88C0B31117B
```

```xml
<group name="system">
# version: {{ version }}{{ ignore('.*') }}
# model = {{ model }}
# serial number = {{ serial_number }}
</group>
```

Example for Keenetic:

```text
! release: 4.1.7.1-1
! model: Keenetic Extra
! hw_version: F02B4E7A1C90
```

```xml
<group name="system">
! release: {{ version }}
! model: {{ model | ORPHRASE }}
! hw_version: {{ serial_number }}
</group>
```

## The interfaces Group

The `interfaces` group must return a list of dictionaries. Each dictionary
describes one interface.

The `Interfaces` contract expects these fields:

| Contract field | TTP name / alias | Type | Required |
| --- | --- | --- | --- |
| `name` | `interface` | `str` | Yes |
| `ip_address` | `ip_address` | `IPv4Address | None` | No |
| `mask` | `mask` | `int | None` | No |
| `description` | `description` | `str | None` | No |

The Pydantic field `name` has the alias `interface`, so templates should usually
emit `interface`. You can also emit `name` because the models allow population
by field name, or you can normalize keys in the device class by overriding
`interfaces()`.

Example for MikroTik:

```text
/ip address
add address=192.168.1.1/24 interface=ether1 network=192.168.1.0
add address=10.0.0.1/30 comment="WAN link" interface=ether2 network=10.0.0.0
```

```xml
<group name="interfaces">
/ip address
add address={{ ip_address | _start_ }}/{{ mask }} interface={{ interface }} network={{ network }}
add address={{ ip_address | _start_ }}/{{ mask }} comment={{ description | ORPHRASE | strip('"') }} interface={{ interface }} network={{ network }}
</group>
```

Example for CLI-style devices:

```text
interface Vlanif120
 description SSH
 ip address 10.26.196.254 255.255.255.0
```

```xml
<group name="interfaces">
interface {{ interface | _start_ }}
 description {{ description | ORPHRASE }}
 ip address {{ ip_address }} {{ mask | to_cidr }}
</group>
```

Use TTP's `to_cidr` formatter when the device uses dotted decimal masks.

## The vlans Group

The `vlans` group is optional. If it is declared, it must return a list of VLAN
dictionaries.

The `Vlans` contract expects these fields:

| Contract field | Alias | Type | Required |
| --- | --- | --- | --- |
| `vlan_id` | none | `int` | Yes |
| `name` | `description` | `str | None` | No |

`name` has the alias `description`, so either key is accepted. Existing parsers
use both forms depending on the vendor format.

Example:

```text
vlan 10
 name MGMT
```

```xml
<group name="vlans">
vlan {{ vlan_id | _start_ }}
 name {{ name | ORPHRASE }}
</group>
```

For compressed vendor syntax such as `vlan batch 101 to 103 110`, parse the raw
range in the template and normalize it in the device class when needed.

## Useful TTP Features

### Line markers

| Marker | Description |
| --- | --- |
| `_start_` | Starts a new group match from the current line. |
| `_end_` | Ends the current group match. |

```xml
interface {{ interface | _start_ }}
```

### Variable modifiers

| Modifier | Description |
| --- | --- |
| `ORPHRASE` | Captures a word or phrase to the end of the line. |
| `exclude("pattern")` | Skips the match when the captured value contains the pattern. |
| `strip('"')` | Removes a character from both ends of the captured value. |
| `replace("old","new")` | Replaces text inside the captured value. |
| `re("pattern")` | Accepts the value only if it matches the regex. |
| `ignore` | Captures and discards the value. |
| `ignore('.*')` | Discards the rest of the line. |
| `to_cidr` | Converts a dotted decimal netmask to a prefix length. |
| `unrange("-", ",")` | Expands ranges such as `10-12` using a comma separator. |
| `split(",")` | Splits a captured string into a list. |

### Template comments

Lines beginning with `##` are TTP comments:

```xml
## disabled no comment
add address={{ ip_address | _start_ }}/{{ mask }} interface={{ interface }}
```

## Default Variables

The `<vars>` block can define default values for a group through the group's
`default` attribute:

```xml
<vars>
default_system = {
    "model": "",
    "serial_number": "",
    "version": ""
}
</vars>

<group name="system" default="default_system">
# version: {{ version }}
# model = {{ model }}
# serial number = {{ serial_number }}
</group>
```

If the group does not match anything, TTP returns the default dictionary.

## Full Example

This simplified Cisco IOS-style example shows the expected shape of a complete
template:

```xml
<doc>
Cisco IOS running-config parser.
</doc>

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
 ip address {{ ip_address }} {{ mask | to_cidr }}
</group>

<group name="vlans">
vlan {{ vlan_id | _start_ }}
 name {{ name | ORPHRASE }}
</group>
```

## Validation

`BaseDevice` performs two validation passes:

1. Template structure validation checks that the template declares the required
   `system` and `interfaces` groups.
2. Parse result validation checks that TTP actually returned the required groups
   for the given configuration.

After that, parsed data is validated by Pydantic models from
`oxi.interfaces.contract`. Invalid structures raise the original Pydantic
validation error.
