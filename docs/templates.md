# Написание TTP-шаблонов

oxipy использует библиотеку [TTP (Template Text Parser)](https://ttp.readthedocs.io/) для парсинга конфигураций сетевых устройств в структурированные данные. Шаблоны хранятся в директории `oxi/interfaces/models/templates/`.

## Содержание

- [Структура шаблона](#структура-шаблона)
- [Обязательные группы](#обязательные-группы)
- [Секция system](#секция-system)
- [Секция interfaces](#секция-interfaces)
- [Секция vlans](#секция-vlans)
- [TTP: основные возможности](#ttp-основные-возможности)
- [Переменные по умолчанию](#переменные-по-умолчанию)
- [Практические примеры](#практические-примеры)
- [Валидация шаблона](#валидация-шаблона)

---

## Структура шаблона

Каждый шаблон — это `.ttp`-файл, состоящий из следующих блоков:

```xml
<doc>
    Описание шаблона (опционально)
</doc>

<vars>
    <!-- Переменные по умолчанию для групп -->
</vars>

<group name="system">
    <!-- Правила для системной информации -->
</group>

<group name="interfaces">
    <!-- Правила для интерфейсов -->
</group>

<group name="vlans">
    <!-- Правила для VLAN (опционально) -->
</group>
```

Файл-заготовка находится в `oxi/interfaces/models/templates/_template.ttp`.

---

## Обязательные группы

Фреймворк требует наличия в шаблоне **двух обязательных групп**:

| Группа       | Обязательна | Описание                      |
|--------------|-------------|-------------------------------|
| `system`     | Да          | Системная информация          |
| `interfaces` | Да          | Конфигурация интерфейсов      |
| `vlans`      | Нет         | Конфигурация VLAN             |

Если обязательная группа отсутствует в шаблоне или TTP не вернул её данные, будет выброшено `ValueError`.

---

## Секция system

Должна возвращать словарь со следующими полями:

| Поле            | Тип  | Обязательное | Описание            |
|-----------------|------|--------------|---------------------|
| `model`         | str  | Да           | Модель устройства   |
| `serial_number` | str  | Да           | Серийный номер      |
| `version`       | str  | Да           | Версия прошивки     |

**Пример (MikroTik):**

Конфигурация:
```
# version: 7.12.1 (stable)
# model = RB951Ui-2nD
# serial number = B88C0B31117B
```

Шаблон:
```
<group name="system">
# version: {{ version }}{{ ignore('.*') }}
# model = {{ model }}
# serial number = {{ serial_number }}
</group>
```

**Пример (Keenetic):**

Конфигурация:
```
! release: 4.1.7.1-1
! model: Keenetic Extra
! hw_version: F02B4E7A1C90
```

Шаблон:
```
<group name="system">
! release: {{ version }}
! model: {{ model | ORPHRASE }}
! hw_version: {{ serial_number }}
</group>
```

---

## Секция interfaces

Должна возвращать список словарей. Каждый словарь описывает один интерфейс.

Поля, которые ожидает контракт `Interfaces`:

| Поле          | TTP-имя / alias | Тип              | Обязательное |
|---------------|-----------------|------------------|--------------|
| `name`        | `interface`     | str              | Да           |
| `ip_address`  | `ip_address`    | IPv4Address      | Нет          |
| `mask`        | `mask`          | int (prefix len) | Нет          |
| `description` | `description`   | str              | Нет          |

> **Важно:** поле `name` в Pydantic-модели имеет алиас `interface`, поэтому в шаблоне переменную нужно называть именно `interface` **или** переопределить метод `interfaces()` в классе модели (см. [Расширение моделей](extending-models.md)).

**Пример (MikroTik):**

Конфигурация:
```
/ip address
add address=192.168.1.1/24 interface=ether1 network=192.168.1.0
add address=10.0.0.1/30 comment="WAN link" interface=ether2 network=10.0.0.0
```

Шаблон:
```
<group name="interfaces">
/ip address
add address={{ ip_address | _start_ }}/{{ mask }} interface={{ interface }} network={{ network }}
add address={{ ip_address | _start_ }}/{{ mask }} comment={{ description | ORPHRASE | strip('"') }} interface={{ interface }} network={{ network }}
</group>
```

**Пример (Keenetic):**

Конфигурация:
```
interface GigabitEthernet0/0
    description "WAN"
    ip address 10.0.0.2 255.255.255.252
interface GigabitEthernet0/1
    ip address 192.168.1.1 255.255.255.0
```

Шаблон:
```
<group name="interfaces">
interface {{ name | _start_ | exclude("Vlan") }}
    description {{ description | ORPHRASE }}
    ip address {{ ip_address }} {{ netmask }}
</group>
```

Здесь переменная называется `name`, а не `interface` — это покрывается переопределением метода `interfaces()` в классе `Keenetic`.

---

## Секция vlans

Необязательная группа. Если объявлена в шаблоне, фреймворк ожидает её наличия в результате TTP.

Поля контракта `Vlans`:

| Поле      | TTP-имя / alias | Тип  | Обязательное |
|-----------|-----------------|------|--------------|
| `vlan_id` | `id`            | int  | Да           |
| `name`    | `description`   | str  | Нет          |

> `vlan_id` имеет алиас `id`, поэтому в шаблоне переменная должна называться `id` либо переименовываться в методе `vlans()`.

**Пример (Keenetic):**

Конфигурация:
```
interface Bridge0/Vlan10
    description "MGMT"
interface Bridge0/Vlan20
    description "SERVERS"
```

Шаблон:
```
<group name="vlans">
interface {{ ignore }}/Vlan{{ id }}
    description {{ description | ORPHRASE | strip('"') }}
</group>
```

---

## TTP: основные возможности

### Маркеры строк

| Маркер      | Описание                                                      |
|-------------|---------------------------------------------------------------|
| `_start_`   | Строка с этой переменной считается началом нового совпадения  |
| `_end_`     | Строка с этой переменной завершает совпадение группы          |

```
add address={{ ip_address | _start_ }}/{{ mask }} interface={{ name }}
```

### Модификаторы переменных

| Модификатор            | Описание                                                  |
|------------------------|-----------------------------------------------------------|
| `ORPHRASE`             | Захватывает одно слово или фразу (до конца строки)        |
| `exclude("pattern")`   | Пропускает строку, если захваченное значение содержит паттерн |
| `strip('"')`           | Удаляет символ из начала и конца захваченного значения    |
| `replace("old","new")` | Заменяет подстроку в захваченном значении                 |
| `re("pattern")`        | Принимает значение, только если оно соответствует regex   |
| `ignore`               | Захватывает, но игнорирует значение (не включает в результат) |
| `ignore('.*')`         | Игнорирует всё до конца строки                            |

### Комментарии в шаблоне

Строки, начинающиеся с `##`, — это комментарии TTP и не влияют на парсинг:

```
## disabled no comment
add address={{ ip_address | _start_ }}/{{ mask }} interface={{ name }}
```

---

## Переменные по умолчанию

Блок `<vars>` позволяет задавать значения по умолчанию для группы через атрибут `default`:

```xml
<vars>
default_system = {
    "model": "",
    "serial_number": ""
}
</vars>

<group name="system" default="default_system">
# version: {{ version }}
# model = {{ model }}
# serial number = {{ serial_number }}
</group>
```

Если шаблон не нашёл совпадений для группы, будет возвращён словарь из `default_system`.

---

## Практические примеры

### Полный шаблон для нового устройства (пример: Cisco IOS)

```xml
<doc>
    Шаблон для парсинга Cisco IOS running-config
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
 ip address {{ ip_address }} {{ netmask }}
 shutdown {{ shutdown | set("True") }}
</group>

<group name="vlans">
vlan {{ id | _start_ }}
 name {{ description }}
</group>
```

---

## Валидация шаблона

Фреймворк автоматически выполняет два уровня проверки:

1. **Валидация структуры шаблона** — при создании объекта устройства парсятся XML-теги `<group>` и проверяется наличие обязательных секций (`system`, `interfaces`).

2. **Валидация результата парсинга** — после запуска TTP проверяется, что обязательные группы действительно присутствуют в результате (т.е. конфигурация содержала соответствующие строки).

При нарушении любого условия выбрасывается `ValueError` с подробным описанием проблемы.
