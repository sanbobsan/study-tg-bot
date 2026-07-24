# Code Review: study-tg-bot

> Автоматическое ревью. Проект: Telegram-бот для управления очередью желающих.

---

## 1. Баги

### 1.1. Баг приоритета операторов в `/trust` и `/untrust`

**Файл:** `bot/handlers/admin.py:367-372`

```python
results.append(
    "✅ Доверяем пользователю id="
    if trusted
    else "❎ Не доверяем пользователю id="
    + f"{user_id}{name_info}{username_info}"
)
```

Приоритет `+` выше, чем `if/else`. Python читает это как:

```
"✅ Доверяем пользователю id=" if trusted else ("❎ Не доверяем..." + f"{user_id}...")
```

При `trusted=True` в результат попадёт строка **без `user_id`**, `name_info`, `username_info` — просто `"✅ Доверяем пользователю id="`.

---

### 1.2. `create_user` — невозможно отличить успех от ошибки

**Файл:** `bot/db/repository.py:28-67`

Три ситуации, две из которых возвращают `None`:

```python
# Пользователь найден → возвращает User
return user

# Пользователь создан → возвращает None
return None

# Ошибка БД → возвращает None
except Exception as e:
    logging.error(e)
    return None
```

Вызывающий код в `start.py:26`:

```python
user: User | None = await create_user(...)
if user is None or user.name is None:
    # Считает "новый пользователь"
```

При ошибке БД бот решит, что пользователь новый, и предложит ввести имя. Ошибка молча проглатывается.

---

### 1.3. N+1 запрос в построении текста очереди

**Файл:** `bot/utils/queue.py:106`

```python
users: list[User | None] = [await get_user(tg_id) for tg_id in self._queue]
```

Каждый `get_user` открывает **новую сессию БД** через декоратор `@connection`. Очередь из 50 пользователей = 50 отдельных соединений с PostgreSQL.

---

### 1.4. `load_from_file` не очищает очередь перед загрузкой

**Файл:** `bot/utils/queue.py:357-363`

```python
async def load_from_file(self) -> None:
    queues_dict = await load_queues()
    for queue_name, tg_ids in queues_dict.items():
        queue = Queue(queue_name)
        await queue.set_queue(tg_ids, queue_name=queue_name)
        self._queues[queue_name] = queue  # Перезаписывает, но не удаляет старые
```

Если администратор удалил очередь и нажал `/load` — удалённая очередь воскреснет из JSON-файла.

---

### 1.5. `IsTrustedMiddleware` — хрупкое тернарное выражение

**Файл:** `bot/middlewares/middlewares.py:33`

```python
if user.trusted if user else False:
```

Работает, но нечитаемо. Если рефакторить — легко получить `AttributeError` на `None`. Должно быть `if user and user.trusted:`.

---

### 1.6. `commit()` и `refresh()` при существующем пользователе

**Файл:** `bot/db/repository.py:49-50`

```python
if user is not None:
    await session.commit()     # Ничего не менялось
    await session.refresh(user) # И это тоже
    return user
```

Лишняя транзакция на пустом месте.

---

### 1.7. `session.close()` избыточен

**Файл:** `bot/db/database.py:51`

`async with async_session() as session` уже закрывает сессию. Явный `close()` в `finally` — дублирование.

---

## 2. Архитектура

### 2.1. `utils/` содержит бизнес-логику

`queue.py` (менеджер очередей) и `broadcaster.py` (рассылка) — это **бизнес-логика**, а не утилиты. Их расположение в `utils/` затрудняет навигацию и нарушает SRP.

**Правильная структура:**

```
bot/
  core/          — ядро (bot, dp)
  db/            — модели и репозиторий
  services/      — бизнес-логика (QueueService, BroadcastService)
  handlers/      — хендлеры (чистая доставка)
  keyboards/
  filters/
  middlewares/
```

---

### 2.2. `Queue` — God Object

`Queue` в `queue.py` одновременно:

- **Модель данных** — хранит список `tg_id`, кеш текста, название
- **Сервис** — выполняет `shuffle()`, `move()`, `replace()`, `next_desiring()`
- **Репозиторий** — обращается к БД через `init_from_db()` и `get_user()` в `next_desiring`
- **Форматер** — строит текст через `_build_queue_text()`

Класс, отвечающий за всё, невозможно тестировать, переиспользовать и поддерживать.

**Как надо:**

- `QueueData` — чистая модель данных (список ID, название, кеш)
- `QueueService` — бизнес-логика (shuffle, move, replace, next)
- `QueueRepository` — персистентность (load/save)
- `QueueFormatter` — форматирование текста

---

### 2.3. `QueueManager` — God Object

374 строки, делает:

- CRUD очередей (create, copy, delete, list, set_current)
- Операции над очередями (show, shuffle, move, replace, next, init)
- Персистентность (load_from_file, save_to_file)
- Форматирование отчётов (_build_queue_report)
- Кеширование текста

При добавлении нового типа операции придётся лезть в монолитный класс.

---

### 2.4. `admin.py` — 420 строк, 20+ хендлеров

Все админ-хендлеры в одном файле. Текст help-команд (строки 24-54) написан вручную и дублирует реальные декораторы. При добавлении команды нужно:
1. Написать хендлер
2. Добавить строку в `admin_panel`

Забыл второе — help будет неполным.

**Как надо:** Разбить по домену:

- `handlers/admin/queues.py` — управление очередями
- `handlers/admin/users.py` — управление пользователями
- `handlers/admin/settings.py` — настройки бота

Help генерировать динамически из реестра команд.

---

### 2.5. Нет dependency injection

Все зависимости — глобальные синглтоны: `bot`, `dp`, `queue_manager`, `settings`. Единственная попытка DI — `IsTrustedMiddleware(get_user_func=get_user)` — хорошая идея, но реализованная неудачно.

**Как надо:** Использовать `dp.workflow_data` для передачи зависимостей в хендлеры.

---

### 2.6. Репозиторий глотает исключения

Все функции в `repository.py`:

```python
except Exception as e:
    logging.error(e)
    return None
```

Вызывающий код не может отличить "пользователь не найден" от "БД недоступна". Бот работает "тихо неправильно" — показывает пустые очереди, теряет данные.

**Как надо:** Репозиторий выбрасывает исключения. Обработка — на уровне выше.

---

### 2.7. `update_user` и `update_user_by_id` — дублирование

Разница — одно поле в `filter_by`: `tg_id` vs `id`. Весь остальной код дублируется.

---

### 2.8. `_apply_user_updates` — side effect

**Файл:** `bot/db/repository.py:124-138`

Функция делает `logging.info` при смене имени и trust. Это side effect в функции, которая должна быть чистым применением данных к модели.

---

## 3. Проблемы кода

### 3.1. Дублирование парсинга аргументов

`command.args.split() if command.args else []` повторяется **7 раз** в `admin.py`. Стоило вынести в хелпер.

---

### 3.2. Дублирование текстов ошибок

Одни и те же блоки ошибок копируются между хендлерами. Стоило вынести в константы.

---

### 3.3. `F.text` избыточен рядом с `Command()`

В aiogram 3 `Command("create")` уже фильтрует по текстовым сообщениям.

---

### 3.4. Неверный docstring

**Файл:** `bot/utils/json_storage.py:62`

```python
async def save_bot_settings(settings: BotSettings) -> None:
    """Сохраняет очереди в файл"""  # ← Это настройки бота
```

---

### 3.5. `format_user` определена внутри хендлера

**Файл:** `bot/handlers/admin.py:205-219`

Вложенная функция не использует замыкание, должна быть вынесена на уровень модуля.

---

### 3.6. `bot/` без `__init__.py`

Используется как namespace package. Неявно, может сломаться при рефакторинге или добавлении тестов.

---

### 3.7. Неконсистентный логирование

Одни места — `logging.error(e)`, другие — `logger = logging.getLogger(__name__)`. Стоило выбрать один подход.

---

## 4. Что сделано хорошо

### 4.1. Pydantic-settings

Чистое решение с валидацией, `SecretStr` для пароля, `field_validator` для `admins`.

### 4.2. Alembic миграции

Даже для простой схемы из одной таблицы — правильная практика.

### 4.3. FSM для регистрации

Корректное использование `StatesGroup` и `FSMContext`. Есть кнопка отмены.

### 4.4. Middleware для проверки доступа

Хорошая абстракция: проверка вынесена из хендлеров.

### 4.5. Роутеризация

Чистая组装 роутеров в `handlers/__init__.py`. Порядок подключения осознанный.

### 4.6. Кеш текста очереди

`_cached_text` — хорошая оптимизация. Не нужно пересчитывать при каждом `/menu`.

### 4.7. JSON для очередей

Разумный компромисс для масштаба проекта. Очередь — по сути JSON-массив.

### 4.8. `GetQueueContext`

Хорошая паттерна для передачи контекста поиска очереди.

---

## 5. Как надо было сделать

### 5.1. Структура

```
bot/
  core/
    __init__.py
    bot.py
  db/
    __init__.py
    engine.py
    models.py
    repository.py       # С исключениями, не с None
  services/
    __init__.py
    queue_service.py
    broadcast.py
  handlers/
    __init__.py
    start.py
    register.py
    menu.py
    admin/
      __init__.py
      queues.py
      users.py
      settings.py
  keyboards/
  filters/
  middlewares/
```

### 5.2. Queue как чистая модель

```python
@dataclass
class QueueData:
    name: str
    tg_ids: list[int] = field(default_factory=list)
    cached_text: str = ""
```

Никаких обращений к БД, никакой бизнес-логики. Только данные.

### 5.3. Repository с исключениями

```python
class UserNotFoundError(Exception):
    pass

async def get_user(tg_id: int) -> User:
    user = await session.scalar(...)
    if user is None:
        raise UserNotFoundError(f"User with tg_id={tg_id} not found")
    return user
```

### 5.4. Batch-запросы

```python
async def get_users_by_tg_ids(tg_ids: list[int]) -> list[User]:
    result = await session.scalars(
        select(User).filter(User.tg_id.in_(tg_ids))
    )
    return list(result.all())
```

### 5.5. DI через `dp.workflow_data`

```python
# main.py
dp.workflow_data["queue_manager"] = queue_manager

# handlers
async def handler(message: Message, **data):
    qm: QueueManager = data["queue_manager"]
```

### 5.6. Atomic writes для JSON

```python
async def save_queues(data: dict) -> None:
    tmp_path = QUEUES_FILE_PATH + ".tmp"
    async with aiofiles.open(tmp_path, "w") as f:
        await f.write(json.dumps(data, indent=4))
    os.replace(tmp_path, QUEUES_FILE_PATH)
```

### 5.7. Rate limiting в broadcaster

```python
async def send(message_text: str, trusted_only: bool = True) -> None:
    users = await get_users(...)
    for i, user in enumerate(users):
        await bot.send_message(user.tg_id, text=message_text)
        if i % 30 == 29:
            await asyncio.sleep(1)
```

---

## 6. Итог

| Аспект | Оценка |
|--------|--------|
| Выбор стека | Отлично |
| Структура проекта | Удовл. |
| Бизнес-логика | Удовл. |
| Обработка ошибок | Плохо |
| Тестирование | Нет |
| Безопасность | Удовл. |
| Документация | Хорошо |
| Баги | Критично |

**Вердикт:** Проект показывает понимание основ Telegram-бот разработки и базовых паттернов. Главные проблемы — баги в коде и архитектурные компромиссы (God Object, глотание исключений). Ключевой takeaway: **разделяй модель данных от бизнес-логики, не глотай исключения, и всегда проверяй приоритет операторов в Python.**
