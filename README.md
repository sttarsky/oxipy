# oxipy

Python-клиент для работы с Oxidized API — системой управления конфигурацией сетевых устройств. Предоставляет удобный интерфейс для получения конфигураций узлов, их парсинга и работы с результатами.

## Содержание

- [Установка](#установка)
- [Быстрый старт](#быстрый-старт)
- [API Reference](#api-reference)
  - [OxiAPI](#oxiapi)
  - [NodeView](#nodeview)
  - [NodeConfig](#nodeconfig)
  - [ModelView](#modelview)
- [Поддерживаемые устройства](#поддерживаемые-устройства)
- [Дополнительно](#дополнительно)

---

## Установка

> Пакет распространяется через Gitea Package Registry и исходники репозитория.
> В PyPI пакет не публикуется.

**Требования:** Python 3.11+

### Из Gitea Package Registry

Добавьте registry в конфигурацию pip и установите пакет:

```bash
pip install oxipy \
  --index-url https://gitea.imbastark.ru/api/packages/Netbox/pypi/simple/
```

Или пропишите registry постоянно в `pip.conf` / `pip.ini`, чтобы не указывать `--index-url` каждый раз:

```ini
# ~/.config/pip/pip.conf  (Linux/macOS)
# %APPDATA%\pip\pip.ini   (Windows)

[global]
extra-index-url = https://gitea.imbastark.ru/api/packages/Netbox/pypi/simple/
```

После этого достаточно:

```bash
pip install oxipy
```

Если registry требует аутентификации, передайте токен:

```bash
pip install oxipy \
  --index-url https://__token__:<your_token>@gitea.imbastark.ru/api/packages/Netbox/pypi/simple/
```

### Из репозитория Gitea

Установка напрямую через pip без клонирования:

```bash
pip install git+https://gitea.imbastark.ru/Netbox/oxipy.git
```

Конкретный тег или ветка:

```bash
pip install git+https://gitea.imbastark.ru/Netbox/oxipy.git@v0.1.0
pip install git+https://gitea.imbastark.ru/Netbox/oxipy.git@dev
```

Для разработки (editable install):

```bash
git clone https://gitea.imbastark.ru/Netbox/oxipy
cd oxipy
pip install -e .
```

---

## Быстрый старт

```python
from oxi import OxiAPI

api = OxiAPI(url="https://oxi.example.com", verify=False)

node = api.node("Router_HOME")

print(node.ip)          
print(node.model)       
print(node.full_name)   

>>> 192.168.1.1
>>> keenetic
>>> router/HQ

print(node.config.system.model)
print(node.config.interfaces.json())
print(node.config.vlans.json())

>>> Sprinter (KN-3710)
>>> 
[
    {"name":"Bridge1","ip_address":"192.168.1.1","mask":24,"description":"\"Guest network\""},
    {"name":"Bridge0","ip_address":"172.16.1.1","mask":24,"description":"\"Home network\""}
]
>>> 
[
    {"vlan_id":1,"name":"Home VLAN"},
    {"vlan_id":2,"name":"Подключение Ethernet"},
    {"vlan_id":3,"name":"Home network"}
]
```

---

## API Reference

### OxiAPI

Точка входа. Управляет HTTP-сессией и предоставляет доступ к узлам.

```python
OxiAPI(
    url: str,
    username: str | None = None,
    password: str | None = None,
    verify: bool = True,
)
```


| Параметр   | Тип    | Описание                                                  |
| ---------- | ------ | --------------------------------------------------------- |
| `url`      | `str`  | Базовый URL Oxi API, например `https://oxi.example.com`   |
| `username` | `str`  | Имя пользователя для базовой аутентификации (опционально) |
| `password` | `str`  | Пароль для базовой аутентификации (опционально)           |
| `verify`   | `bool` | Проверять SSL-сертификат. `True` по умолчанию             |


**Пример:**

```python
# Без аутентификации
api = OxiAPI(url="https://oxi.example.com")

# С базовой аутентификацией
api = OxiAPI(
    url="https://oxi.example.com",
    username="admin",
    password="secret",
)

# Использование как контекстного менеджера (автоматически закрывает сессию)
with OxiAPI(url="https://oxi.example.com") as api:
    node = api.node("HQ")
    print(node.ip)

>>>  192.168.1.1
```

#### `api.node(name)`

Возвращает `[NodeView](#nodeview)` для указанного узла.

```python
node = api.node("HQ")
```

---

### NodeView

Представление узла сети. Содержит метаданные и ленивый доступ к конфигурации.


| Свойство    | Тип          | Описание                                             |
| ----------- | ------------ | ---------------------------------------------------- |
| `ip`        | `str`        | IP-адрес узла                                        |
| `full_name` | `str`        | Полное имя узла в Oxi                                |
| `group`     | `str`        | Группа, к которой принадлежит узел                   |
| `model`     | `str`        | Модель устройства (используется для парсинга)        |
| `config`    | `NodeConfig` | Конфигурация узла (загружается при первом обращении) |


**Пример:**

```python
node = api.node("HQ")

print(node.ip)
print(node.group)
print(node.model)

>>> 192.168.1.1
>>> branch-office
>>> keenetic
```

---

### NodeConfig

Загружает и парсит конфигурацию устройства. Использует TTP-шаблоны, соответствующие модели устройства.

Доступ к секциям конфигурации осуществляется через свойства, возвращающие `[ModelView](#modelview)`.


| Свойство     | Возвращает                    | Описание                           |
| ------------ | ----------------------------- | ---------------------------------- |
| `system`     | `ModelView[System]`           | Системная информация об устройстве |
| `interfaces` | `ModelView[list[Interfaces]]` | Список интерфейсов                 |
| `vlans`      | `ModelView[list[Vlans]]`      | Список VLAN (если есть)            |
| `text`       | `str`                         | Сырой текст конфигурации           |


**Пример:**

```python
cfg = node.config

# Системная информация
print(cfg.system.model)          
print(cfg.system.serial_number)  
print(cfg.system.version)        

>>> Mikrotik RB951Ui-2nD
>>> B88C0B31117B
>>> 7.16.1

# Итерация по интерфейсам
for iface in cfg.interfaces:
    print(iface.name, iface.ip_address, iface.mask)

# Индексация
first_iface = cfg.interfaces[0]
print(first_iface.name)

# Количество интерфейсов
print(len(cfg.interfaces))

# JSON-дамп любой секции
print(cfg.interfaces.json())
print(cfg.vlans.json())
print(cfg.system.json())

# Сырая конфигурация текстом
print(cfg.text)
```

---

### ModelView

Обёртка над Pydantic-моделью или списком моделей. Обеспечивает сериализацию, итерацию и прозрачный доступ к атрибутам.


| Метод / свойство | Применимо к  | Описание                                          |
| ---------------- | ------------ | ------------------------------------------------- |
| `.json()`        | оба варианта | Возвращает JSON-строку (с `by_alias=True`)        |
| `.<attr>`        | оба варианта | Проксирует обращение к атрибутам вложенной модели |
| `iter(view)`     | список       | Итерация по элементам списка моделей              |
| `len(view)`      | список       | Количество элементов в списке                     |
| `view[i]`        | список       | Получение элемента по индексу или срез            |


> `__iter__`, `__len__` и `__getitem__` доступны только для `interfaces` и `vlans` (они оборачивают список). Вызов этих методов на `system` (одиночная модель) вызовет `TypeError`.

**Примеры:**

```python
# Одиночная модель — system
view = node.config.system
print(view.json())
>>> '{"model":"RB951Ui-2nD","serial_number":"B88C0B31117B","version":"7.12.1"}'
print(view.model)          # 'RB951Ui-2nD'
print(view.serial_number)  # 'B88C0B31117B'

>>> RB951Ui-2nD
>>> B88C0B31117B
# Список — interfaces
interfaces = node.config.interfaces

# Итерация
for iface in interfaces:
    print(iface.name, iface.ip_address)

# Длина
print(len(interfaces))   # 5

# Индексация и срезы
first = interfaces[0]
top3 = interfaces[:3]

# JSON всего списка
print(interfaces.json())
```

---

## Поддерживаемые устройства


| Устройство | Ключи реестра                    |
| ---------- | -------------------------------- |
| Keenetic   | `ndms`, `keenetic`, `keeneticos` |
| MikroTik   | `routeros`, `ros`, `mikrotik`    |
| Qtech      | `qtech`                          |
| Huawei     | `huawei`, `vrp`                  |
| Eltex      | `eltex`                          |
| H3C        | `h3c`                            |
| Quasar     | `qos`, `quasar`                  |


Ключи реестра — это значения поля `model`, возвращаемого API для узла. Регистр не учитывается.

Добавить поддержку нового устройства можно самостоятельно — подробнее в разделе [Расширение моделей](docs/extending-models.md).

---

## Дополнительно

- [Написание TTP-шаблонов](docs/templates.md)
- [Расширение и переопределение моделей устройств](docs/extending-models.md)

