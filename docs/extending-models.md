# Расширение и переопределение моделей устройств

oxipy предоставляет гибкий механизм расширения через наследование от `BaseDevice`. После того как TTP-шаблон разобрал конфигурацию в сырой словарь `self.raw`, данные проходят через три метода экземпляра — `system()`, `interfaces()`, `vlans()` — перед тем как попасть в контракт. Переопределяя эти методы, можно трансформировать, фильтровать и обогащать данные без изменения шаблона или контракта.

## Содержание

- [Архитектура: путь данных](#архитектура-путь-данных)
- [Регистрация нового устройства](#регистрация-нового-устройства)
- [Переопределение методов (monkey patching)](#переопределение-методов-monkey-patching)
  - [interfaces()](#interfaces)
  - [vlans()](#vlans)
  - [system()](#system)
- [Полный пример: новое устройство](#полный-пример-новое-устройство)
- [Контракт: ожидаемые структуры](#контракт-ожидаемые-структуры)

---

## Архитектура: путь данных

```
текст конфигурации
        │
        ▼
   TTP-шаблон (.ttp)
        │  парсит в сырой словарь
        ▼
   self.raw: dict
        │
        ├──► system()     → dict
        ├──► interfaces() → list[dict]
        └──► vlans()      → list[dict]
                │
                ▼
        _validate_contract()
                │  создаёт Pydantic-модели
                ▼
           Device(system, interfaces, vlans)
```

Методы `system()`, `interfaces()`, `vlans()` — это точки расширения. Базовая реализация просто возвращает данные из `self.raw`:

```python
# BaseDevice (упрощённо)
def interfaces(self) -> list[dict]:
    return self.raw.get("interfaces", [])

def vlans(self) -> list[dict]:
    return self.raw.get("vlans", [])

def system(self) -> dict:
    return self.raw.get("system", None)
```

---

## Регистрация нового устройства

Чтобы добавить поддержку нового вендора:

1. Создайте файл в `oxi/interfaces/models/`, например `cisco.py`.
2. Создайте шаблон `oxi/interfaces/models/templates/cisco.ttp`.
3. Унаследуйте класс от `BaseDevice` и зарегистрируйте его декоратором `@register_parser`.

```python
# oxi/interfaces/models/cisco.py
from oxi.interfaces import register_parser
from oxi.interfaces.base import BaseDevice


@register_parser(["ios", "cisco", "cisco_ios"])
class CiscoIOS(BaseDevice):
    template = "cisco.ttp"
```

Декоратор `@register_parser` принимает список строк — это ключи, по которым устройство ищется в реестре. Поле `model` от API сравнивается с этими ключами без учёта регистра.

После добавления файла он автоматически импортируется через `pkgutil` при старте приложения — явно импортировать не нужно.

---

## Переопределение методов (monkey patching)

### interfaces()

Используйте переопределение, когда нужно:

- Преобразовать формат IP-адреса (например, `netmask` → `prefix_length`).
- Декодировать escape-последовательности в описаниях.
- Переименовать ключи, не совпадающие с контрактом.
- Фильтровать служебные интерфейсы.

**Пример: конвертация маски подсети в префикс**

TTP возвращает `netmask` как `255.255.255.0`, а контракт `Interfaces` ожидает `mask` как целое число (prefix length):

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

**Пример: фильтрация служебных интерфейсов**

```python
def interfaces(self) -> list[dict]:
    return [
        item for item in self.raw.get("interfaces", [])
        if not item.get("name", "").startswith("lo")
    ]
```

**Пример: декодирование Unicode escape-последовательностей**

Некоторые устройства (например, Keenetic) хранят кириллические описания как `\xd0\xb8\xd0\xbc\xd1\x8f`:

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

---

### vlans()

Аналогично `interfaces()`. Используйте для нормализации ID, декодирования названий, обогащения данными из других секций.

**Пример: добавление префикса к имени VLAN**

```python
def vlans(self) -> list[dict]:
    result = []
    for item in self.raw.get("vlans", []):
        item["description"] = f"VLAN_{item.get('id', '?')}"
        result.append(item)
    return result
```

**Пример: объединение данных из нескольких секций**

```python
def vlans(self) -> list[dict]:
    vlans = {v["id"]: v for v in self.raw.get("vlans", [])}
    # обогащаем данными из другой секции, если она есть
    for extra in self.raw.get("vlan_details", []):
        vlan_id = extra.get("id")
        if vlan_id in vlans:
            vlans[vlan_id].update(extra)
    return list(vlans.values())
```

---

### system()

Переопределяйте, если структура системной секции отличается от ожидаемой контрактом, или нужно вычислить поля:

**Пример: собрать серийный номер из нескольких полей**

```python
def system(self) -> dict:
    raw_system = self.raw.get("system", {})
    # Устройство возвращает серийный номер в двух частях
    part1 = raw_system.get("serial_part1", "")
    part2 = raw_system.get("serial_part2", "")
    raw_system["serial_number"] = f"{part1}-{part2}"
    return raw_system
```

**Пример: нормализация строки версии**

```python
def system(self) -> dict:
    raw_system = self.raw.get("system", {})
    # Убираем лишнее из "7.12.1 (stable)" → "7.12.1"
    version = raw_system.get("version", "")
    raw_system["version"] = version.split()[0] if version else version
    return raw_system
```

---

## Полный пример: новое устройство

Допустим, нужно добавить поддержку Cisco IOS, где:
- IP-адрес и маска разделены пробелом в конфигурации (`ip address 10.0.0.1 255.255.255.0`).
- Описание интерфейса может содержать несколько слов.
- Серийный номер разделён дефисом в двух строках.

**Шаблон** (`oxi/interfaces/models/templates/cisco.ttp`):

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
vlan {{ id | _start_ }}
 name {{ description }}
</group>
```

**Класс устройства** (`oxi/interfaces/models/cisco.py`):

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
            # Конвертируем маску подсети в длину префикса
            if item.get("ip_address") and item.get("netmask"):
                iface = ip_interface(f"{item['ip_address']}/{item['netmask']}")
                item["mask"] = iface.network.prefixlen
                item.pop("netmask", None)
            # Фильтруем интерфейсы управления
            if item.get("interface", "").startswith("Mgmt"):
                continue
            result.append(item)
        return result

    def system(self) -> dict:
        raw_system = self.raw.get("system", {})
        # Нормализуем версию: "15.2(4)M3" → оставляем как есть
        # Убираем лишние пробелы в модели
        if raw_system.get("model"):
            raw_system["model"] = raw_system["model"].strip()
        return raw_system
```

---

## Контракт: ожидаемые структуры

Методы должны возвращать данные в следующем формате. Контракт жёстко проверяется Pydantic.

### `system()` → `dict`

```python
{
    "model": "RB951Ui-2nD",       # str, обязательно
    "serial_number": "B88C0B31117B",  # str, обязательно
    "version": "7.12.1",          # str, обязательно
}
```

### `interfaces()` → `list[dict]`

```python
[
    {
        "interface": "ether1",          # str, обязательно (alias для поля name)
        "ip_address": "192.168.1.1",    # str | None
        "mask": 24,                     # int | None (длина префикса)
        "description": "LAN",          # str | None
    },
    ...
]
```

### `vlans()` → `list[dict]`

```python
[
    {
        "id": 10,                       # int, обязательно (alias для поля vlan_id)
        "description": "MGMT",         # str | None (alias для поля name)
    },
    ...
]
```

> Если имя ключа в словаре совпадает с **alias** поля Pydantic-модели, а не с именем атрибута — используйте alias. Модели сконфигурированы с `populate_by_name=True`, поэтому принимаются оба варианта.
