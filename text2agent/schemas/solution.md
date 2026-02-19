# Solution Structure Reference

Solution — это верхнеуровневый контейнер, описывающий всего агента (бота).

## Иерархия

```
Solution
├── preprocessing (Scenario, optional)
└── scenarios[]
    └── Scenario
        ├── entry_edges[]
        └── nodes[]
            └── Node
                └── blocks[]
                    └── Block
```

---

## Solution

Корневой объект агента.

```json
{
  "bot_name": "MyBot",
  "request_ttl_in_seconds": 30,
  "no_match_stub_answer": "Извините, я не понял ваш вопрос",
  "need_preprocess": "disabled",
  "preprocessing": null,
  "scenarios": [...]
}
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| bot_name | string | да | Имя бота (4-64 символа) |
| request_ttl_in_seconds | number | да | Таймаут запроса в секундах |
| no_match_stub_answer | string | да | Ответ при отсутствии совпадений (мин 4 символа) |
| need_preprocess | "disabled" \| "optional" \| "required" | да | Режим preprocessing |
| preprocessing | Scenario \| null | нет | Сценарий preprocessing |
| scenarios | Scenario[] | да | Список сценариев |

**need_preprocess:**
- `disabled` — preprocessing отключён
- `optional` — preprocessing опционален
- `required` — preprocessing обязателен (для NLU классификации)

---

## Scenario

Сценарий — набор узлов с правилами активации.

```json
{
  "name": "booking_scenario",
  "slug": "booking",
  "parent_scenario_id": null,
  "entry_edges": [...],
  "nodes": [...]
}
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| name | string | да | Имя сценария |
| slug | string | да (V2/V3) | URL-friendly идентификатор (уникальный) |
| parent_scenario_id | number \| null | нет | ID родительского сценария |
| entry_edges | EntryEdge[] | да | Правила активации |
| nodes | Node[] | да | Узлы сценария |

**slug:** Должен быть уникальным среди всех сценариев версии.

---

## Node

Узел — цепочка блоков для выполнения.

```json
{
  "id": "greeting_node",
  "name": "Приветствие",
  "blocks": [...],
  "next_node_id": "ask_question_node"
}
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| id | string | да | Уникальный ID узла (в рамках сценария) |
| name | string | нет | Человекочитаемое имя |
| blocks | Block[] | да | Список блоков |
| next_node_id | string \| null | нет | ID следующего узла (null = конец) |

**Важно:** `id` должен быть уникальным в рамках сценария.

---

## Поток выполнения

```
User Message → Solution Router → Scenario Router → Node Chain → Response

1. Solution Router:
   - Собирает ActivationCandidates из всех scenarios
   - Выбирает лучший match по score
   - Переходит в целевой scenario

2. Scenario Router:
   - Определяет entry_node из matching edge
   - Запускает цепочку выполнения

3. Node Chain:
   - Выполняет blocks последовательно
   - По завершении → next_node_id или конец

4. Прерывания:
   - WaitForUserBlock → сохраняет состояние, ждёт ввод
   - При новом сообщении → восстанавливает и продолжает
```

---

## Контекст выполнения

Во время выполнения доступны scopes переменных:

### system (readonly)
```
system.last_user_message      — последнее сообщение (lowercase)
system.source_message         — оригинальное сообщение
system.session_id             — ID сессии
system.channel_id             — ID канала
system.current_scenario_id    — ID текущего сценария
system.utc_now_dt             — текущее время (ISO)
system.messages_number        — количество сообщений в сессии
```

### session (read/write, persistent)
```
session.{variable_name}       — пользовательские переменные
```
Сохраняются между сообщениями в рамках сессии.

### request (read/write, per-request)
```
request.{variable_name}       — переменные запроса
```
Очищаются после каждого запроса.

### temp (read/write, temporary)
```
temp.{variable_name}          — временные переменные
```
Очищаются после каждого цикла.

### nlu (readonly)
```
nlu.matches                   — результаты regex matching
nlu.intents                   — результаты intent classification
nlu.rules                     — результаты rule matching
```

---

## Паттерны проектирования

### Linear Flow (линейный)

```
[Node A] → [Node B] → [Node C] → END
```

```json
{
  "nodes": [
    {"id": "a", "blocks": [...], "next_node_id": "b"},
    {"id": "b", "blocks": [...], "next_node_id": "c"},
    {"id": "c", "blocks": [...], "next_node_id": null}
  ]
}
```

### Branching (ветвление)

```
[Node A] → SingleIfBlock → [Node B] (if true)
                        → [Node C] (if false)
```

```json
{
  "nodes": [
    {
      "id": "a",
      "blocks": [
        {"type": "single_if", "expression": "...", "target_node_id": "b"}
      ],
      "next_node_id": "c"
    },
    {"id": "b", "blocks": [...]},
    {"id": "c", "blocks": [...]}
  ]
}
```

### Question-Answer Loop

```
[Ask] → [Wait] → [Process] → [Respond] → [Ask]...
```

```json
{
  "nodes": [
    {
      "id": "ask",
      "blocks": [
        {"type": "answer", "value": "Введите ваш вопрос:"},
        {"type": "wait_for_user"}
      ],
      "next_node_id": "process"
    },
    {
      "id": "process",
      "blocks": [
        {"type": "llm", "user_message": "{{system.last_user_message}}", ...}
      ],
      "next_node_id": "respond"
    },
    {
      "id": "respond",
      "blocks": [
        {"type": "answer", "value": "{{session.llm_response}}"}
      ],
      "next_node_id": "ask"
    }
  ]
}
```

### Multi-Scenario (несколько сценариев)

```
[Main Scenario] ←→ [FAQ Scenario]
                ←→ [Booking Scenario]
                ←→ [Support Scenario]
```

Каждый сценарий имеет свои entry_edges, система автоматически маршрутизирует.

---

## Типичная структура агента

```json
{
  "bot_name": "MyAssistant",
  "request_ttl_in_seconds": 30,
  "no_match_stub_answer": "Извините, я не понял",
  "need_preprocess": "disabled",
  "scenarios": [
    {
      "name": "main",
      "slug": "main",
      "entry_edges": [
        {"type": "event", "value": "init", "target_node_id": "welcome"},
        {"type": "event", "value": "no_match", "target_node_id": "fallback"}
      ],
      "nodes": [
        {
          "id": "welcome",
          "blocks": [
            {"id": "w1", "type": "answer", "value": "Привет! Чем могу помочь?"},
            {"id": "w2", "type": "wait_for_user"}
          ],
          "next_node_id": null
        },
        {
          "id": "fallback",
          "blocks": [
            {"id": "f1", "type": "answer", "value": "Не понял, попробуйте переформулировать"}
          ],
          "next_node_id": null
        }
      ]
    },
    {
      "name": "faq",
      "slug": "faq",
      "entry_edges": [
        {"type": "match", "value": "помощь|help|faq", "target_node_id": "faq_start"}
      ],
      "nodes": [...]
    }
  ]
}
```
