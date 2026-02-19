# Import API Reference

API для импорта агентов в bot-registry.

## Endpoint

```
POST {base_url}/api/v3/bots/import
Content-Type: application/json
```

**base_url** — запрашивается у пользователя при загрузке.

---

## Request Body

```json
{
  "bot_name": "MyBot",
  "author": "text2agent",
  "name": "v1.0",
  "changes_message": "Initial version",
  "request_ttl_in_seconds": 30,
  "no_match_stub_answer": "Извините, я не понял ваш вопрос",
  "need_preprocess": "disabled",
  "model_id": null,
  "preprocessing": null,
  "scenarios": [
    {
      "name": "main",
      "slug": "main",
      "entry_edges": [...],
      "nodes": [...]
    }
  ],
  "layout": null,
  "named_rules": null
}
```

---

## Поля запроса

### Обязательные поля

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| bot_name | string | 4-64 символа | Имя бота |
| author | string | - | Автор (всегда "text2agent") |
| request_ttl_in_seconds | integer | > 0 | Таймаут запроса в секундах |
| no_match_stub_answer | string | >= 4 символа | Ответ при no_match |
| need_preprocess | string | "disabled" \| "optional" \| "required" | Режим preprocessing |
| scenarios | array | >= 1 элемент | Список сценариев |

### Опциональные поля

| Поле | Тип | Default | Описание |
|------|-----|---------|----------|
| name | string \| null | null | Имя версии (макс 32 символа) |
| changes_message | string \| null | null | Описание изменений |
| model_id | integer \| null | null | ID классификатора интентов |
| preprocessing | object \| null | null | Preprocessing сценарий |
| layout | object \| null | null | Layout данные |
| named_rules | object \| null | null | Именованные правила |

---

## Scenario Schema (LanggraphScenarioVersion)

```json
{
  "name": "scenario_name",
  "slug": "unique-slug",
  "parent_scenario_id": null,
  "entry_edges": [
    {
      "type": "event",
      "value": "init",
      "target_node_id": "start_node"
    }
  ],
  "nodes": [
    {
      "id": "start_node",
      "name": "Start",
      "blocks": [
        {
          "id": "block_1",
          "type": "answer",
          "value": "Hello!"
        }
      ],
      "next_node_id": null
    }
  ]
}
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| name | string | да | Имя сценария |
| slug | string | да | Уникальный slug |
| parent_scenario_id | integer \| null | нет | ID родительского сценария |
| entry_edges | array | да | Правила активации |
| nodes | array | да | Узлы сценария |

---

## Response

### Success (200 OK)

```json
{
  "id": 123,
  "bot_id": 456,
  "bot_name": "MyBot",
  "name": "v1.0",
  "author": "text2agent",
  "created_at": "2024-01-15T10:00:00Z",
  "scenarios": [...]
}
```

### Error (4xx/5xx)

```json
{
  "detail": "Error message"
}
```

Типичные ошибки:
- `422` — Validation error (неверные данные)
- `400` — Bad request
- `500` — Internal server error

---

## Пример полного запроса

```json
{
  "bot_name": "FAQ Bot",
  "author": "text2agent",
  "name": "v1.0",
  "changes_message": "Initial FAQ bot",
  "request_ttl_in_seconds": 30,
  "no_match_stub_answer": "Извините, я не могу ответить на этот вопрос",
  "need_preprocess": "disabled",
  "model_id": null,
  "preprocessing": null,
  "scenarios": [
    {
      "name": "main",
      "slug": "main",
      "parent_scenario_id": null,
      "entry_edges": [
        {
          "type": "event",
          "value": "init",
          "target_node_id": "welcome"
        },
        {
          "type": "event",
          "value": "no_match",
          "target_node_id": "fallback"
        }
      ],
      "nodes": [
        {
          "id": "welcome",
          "name": "Welcome Message",
          "blocks": [
            {
              "id": "welcome_msg",
              "type": "answer",
              "value": "Привет! Я FAQ бот. Задайте мне вопрос."
            },
            {
              "id": "wait_input",
              "type": "wait_for_user"
            }
          ],
          "next_node_id": null
        },
        {
          "id": "fallback",
          "name": "Fallback",
          "blocks": [
            {
              "id": "fallback_msg",
              "type": "answer",
              "value": "Попробуйте переформулировать вопрос."
            }
          ],
          "next_node_id": null
        }
      ]
    },
    {
      "name": "hours",
      "slug": "working-hours",
      "parent_scenario_id": null,
      "entry_edges": [
        {
          "type": "match",
          "value": "час.*работ|режим|график|когда открыт",
          "target_node_id": "hours_answer"
        }
      ],
      "nodes": [
        {
          "id": "hours_answer",
          "blocks": [
            {
              "id": "hours_msg",
              "type": "answer",
              "value": "Мы работаем с 9:00 до 18:00, пн-пт."
            }
          ],
          "next_node_id": null
        }
      ]
    }
  ],
  "layout": null,
  "named_rules": null
}
```

---

## cURL пример

```bash
curl -X POST "{base_url}/api/v3/bots/import" \
  -H "Content-Type: application/json" \
  -d '{
    "bot_name": "MyBot",
    "author": "text2agent",
    "request_ttl_in_seconds": 30,
    "no_match_stub_answer": "Не понял",
    "need_preprocess": "disabled",
    "scenarios": [...]
  }'
```
