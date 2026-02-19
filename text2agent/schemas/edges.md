# Entry Edges Reference

Entry Edges — правила активации сценария. Определяют, когда и как пользователь попадает в сценарий.

## Типы Entry Edges

### 1. MatchEdge — Регулярное выражение

Активируется когда сообщение пользователя соответствует regex паттерну.

```json
{
  "id": "match_start",
  "type": "match",
  "value": "/start|начать|привет",
  "target_node_id": "greeting_node",
  "tags": "priority:high"
}
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| id | string | нет | ID ребра (для отладки) |
| type | "match" | да | Тип ребра |
| value | string | да | Regex паттерн (case-insensitive) |
| target_node_id | string | да | ID узла для входа |
| tags | string | нет | Теги (разделённые пробелом) |

**Примеры паттернов:**
- `"/start"` — точное совпадение
- `"привет|здравствуй|добрый день"` — альтернативы
- `"заказ.*доставк"` — частичное совпадение
- `"^отмена$"` — строгое совпадение (начало и конец)

---

### 2. IntentEdge — Классификация интентов

Активируется когда классификатор определяет нужный интент с достаточной уверенностью.

```json
{
  "id": "intent_booking",
  "type": "intent",
  "value": "booking_request",
  "threshold": 0.75,
  "target_node_id": "booking_start",
  "tags": "intent:main"
}
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| id | string | нет | ID ребра |
| type | "intent" | да | Тип ребра |
| value | string | да | Название интента |
| threshold | number | нет | Минимальный score (0-1, default: 0.5) |
| target_node_id | string | да | ID узла для входа |
| tags | string | нет | Теги |

**Важно:** Требует настроенный классификатор (`model_id` в Solution или preprocessing сценарий).

---

### 3. RuleEdge — Правила

Активируется по результатам rule matcher системы.

```json
{
  "id": "rule_complex_condition",
  "type": "rule",
  "value": ["rule_1", "rule_2"],
  "threshold": 0.8,
  "target_node_id": "rule_node",
  "tags": "rule:complex"
}
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| id | string | **да** | ID ребра (обязательно для RuleEdge!) |
| type | "rule" | да | Тип ребра |
| value | array[string] | да | Список ID правил |
| threshold | number | нет | Минимальный score |
| target_node_id | string | да | ID узла для входа |
| tags | string | нет | Теги |

---

### 4. SystemEventEdge — Системные события

Активируется на системные события: инициализация диалога или отсутствие совпадений.

```json
{
  "type": "event",
  "value": "init",
  "target_node_id": "welcome_node"
}
```

```json
{
  "type": "event",
  "value": "no_match",
  "target_node_id": "fallback_node"
}
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| type | "event" | да | Тип ребра |
| value | "init" \| "no_match" | да | Тип события |
| target_node_id | string | да | ID узла для входа |

**События:**
- `init` — первое сообщение в диалоге (is_init=true)
- `no_match` — ни один другой edge не сработал

---

### 5. CustomEventEdge — Пользовательские события

Активируется на кастомные события от внешних систем.

```json
{
  "type": "event",
  "value": "custom",
  "name": "payment_completed",
  "target_node_id": "receipt_node"
}
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| type | "event" | да | Тип ребра |
| value | "custom" | да | Маркер кастомного события |
| name | string | да | Имя события |
| target_node_id | string | да | ID узла для входа |

---

### 6. ManualEdge — Явный переход

Используется для явных переходов (обычно в preprocessing или extend).

```json
{
  "type": "manual",
  "target_node_id": "start_node"
}
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| type | "manual" | да | Тип ребра |
| target_node_id | string | да | ID узла для входа |

**Применение:** Дочерние сценарии, preprocessing, ExtendBlock.

---

## Приоритет активации

Когда несколько edges могут сработать, выбирается по score:

1. **MatchEdge** — score = 1.0 (точное совпадение)
2. **IntentEdge** — score = confidence от классификатора
3. **RuleEdge** — score от rule matcher
4. **SystemEventEdge** — score = 1.0 для `init`, низкий для `no_match`

При равном score — первый в порядке обхода.

---

## Иерархия сценариев

Если у сценария есть `parent_scenario_id`:
- При активации сначала проверяются дочерние сценарии
- Затем текущий сценарий
- Затем родительские

Это позволяет создавать вложенные контексты.

---

## Типичные паттерны

### Приветственный сценарий с fallback

```json
{
  "entry_edges": [
    {
      "type": "event",
      "value": "init",
      "target_node_id": "welcome"
    },
    {
      "type": "match",
      "value": "привет|здравствуй|добрый",
      "target_node_id": "welcome"
    },
    {
      "type": "event",
      "value": "no_match",
      "target_node_id": "fallback"
    }
  ]
}
```

### Сценарий с несколькими интентами

```json
{
  "entry_edges": [
    {
      "type": "intent",
      "value": "booking_create",
      "threshold": 0.7,
      "target_node_id": "create_booking"
    },
    {
      "type": "intent",
      "value": "booking_cancel",
      "threshold": 0.7,
      "target_node_id": "cancel_booking"
    },
    {
      "type": "intent",
      "value": "booking_status",
      "threshold": 0.7,
      "target_node_id": "check_status"
    }
  ]
}
```

### Комбинация match + intent

```json
{
  "entry_edges": [
    {
      "type": "match",
      "value": "/help|помощь",
      "target_node_id": "help_menu"
    },
    {
      "type": "intent",
      "value": "help_request",
      "threshold": 0.6,
      "target_node_id": "help_menu"
    }
  ]
}
```
