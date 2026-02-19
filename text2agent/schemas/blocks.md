# Block Types Reference

Блоки — это атомарные операции внутри узла (Node). Выполняются последовательно.

## 1. AnswerBlock — Отправить сообщение

Отправляет текстовое сообщение пользователю.

```json
{
  "id": "answer_1",
  "type": "answer",
  "value": "Привет! Как я могу помочь?",
  "tts": "<speak>Привет</speak>"
}
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| id | string | да | Уникальный ID блока |
| type | "answer" | да | Тип блока |
| value | string | да | Текст сообщения (поддерживает Handlebars: `{{session.name}}`) |
| tts | string | нет | TTS разметка для голосовых каналов |

---

## 2. WaitForUserBlock — Ожидание ввода

Прерывает выполнение и ждёт следующего сообщения от пользователя.

```json
{
  "id": "wait_1",
  "type": "wait_for_user"
}
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| id | string | да | Уникальный ID блока |
| type | "wait_for_user" | да | Тип блока |

---

## 3. VariablesBlock — Создать/обновить переменную

Вычисляет значение и сохраняет в контекст.

```json
{
  "id": "var_1",
  "type": "variables",
  "name": "user_city",
  "value": "context.system.last_user_message",
  "variable_type": "python"
}
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| id | string | да | Уникальный ID блока |
| type | "variables" | да | Тип блока |
| name | string | да | Имя переменной |
| value | string | да | Значение или выражение |
| variable_type | "constant" \| "python" \| "regexp" \| "regexp_map" | да | Тип вычисления |

**variable_type:**
- `constant` — значение как есть
- `python` — Python выражение
- `regexp` — извлечение по regex
- `regexp_map` — маппинг по regex

---

## 4. ScriptBlock — Выполнить Python код

Выполняет произвольный Python код с доступом к контексту.

```json
{
  "id": "script_1",
  "type": "script",
  "value": "async def handler(context: Context) -> None:\n    message = context.system.source_message\n    context.session['processed'] = message.upper()"
}
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| id | string | да | Уникальный ID блока |
| type | "script" | да | Тип блока |
| value | string | да | Python код с функцией `handler(context)` |

---

## 5. SingleIfBlock — Условный переход

Проверяет условие и переходит на целевой узел если true.

```json
{
  "id": "if_1",
  "type": "single_if",
  "expression": "int(session.get('age', 0)) >= 18",
  "code_type": "python",
  "target_node_id": "adult_content"
}
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| id | string | да | Уникальный ID блока |
| type | "single_if" | да | Тип блока |
| expression | string | да | Python выражение (должно вернуть bool) |
| code_type | "python" | да | Тип кода |
| target_node_id | string | да | ID узла для перехода если true |

Если условие false — переход на `next_node_id` узла.

---

## 6. HttpRequestBlock — HTTP запрос

Отправляет HTTP запрос и маппит ответ в переменные.

```json
{
  "id": "http_1",
  "type": "http_request",
  "url": "https://api.example.com/users/{{session.user_id}}",
  "method": "GET",
  "timeout": 5,
  "headers": [
    {"key": "Authorization", "value": "Bearer {{session.token}}"}
  ],
  "body": null,
  "response_mapping": [
    {
      "key": "user_name",
      "value": "$.data.name",
      "map_to_single_value": true
    }
  ],
  "ok_target_node_id": "success_node",
  "error_target_node_id": "error_node"
}
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| id | string | да | Уникальный ID блока |
| type | "http_request" | да | Тип блока |
| url | string | да | URL (поддерживает Handlebars) |
| method | "GET" \| "POST" \| "PUT" \| "DELETE" \| "PATCH" | да | HTTP метод |
| timeout | number | нет | Таймаут в секундах (default: 5) |
| headers | array | нет | Список заголовков `{key, value}` |
| body | string \| null | нет | Тело запроса (поддерживает Handlebars) |
| response_mapping | array | нет | Маппинг ответа через JSONPath |
| ok_target_node_id | string | нет | Узел при успехе (2xx) |
| error_target_node_id | string | нет | Узел при ошибке |

---

## 7. ButtonsBlock — Кнопки

Отправляет сообщение с кнопками.

```json
{
  "id": "buttons_1",
  "type": "buttons",
  "buttons": [
    {"title": "Да", "target_node_id": "yes_node"},
    {"title": "Нет", "target_node_id": "no_node"},
    {"title": "{{dynamic_option}}"}
  ]
}
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| id | string | да | Уникальный ID блока |
| type | "buttons" | да | Тип блока |
| buttons | array | да | Список кнопок |

**Button:**
| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| title | string | да | Текст кнопки (поддерживает Handlebars) |
| target_node_id | string | нет | Узел для перехода при нажатии |

---

## 8. DynamicButtonsBlock — Динамические кнопки

Создаёт кнопки из переменной (списка или словаря).

```json
{
  "id": "dyn_buttons_1",
  "type": "dynamic_buttons",
  "source_variable_name": "menu_items",
  "result_variable_name": "selected_item",
  "display_text": "Выберите пункт меню:",
  "valid_node_id": "process_selection",
  "invalid_node_id": "invalid_selection"
}
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| id | string | да | Уникальный ID блока |
| type | "dynamic_buttons" | да | Тип блока |
| source_variable_name | string | да | Имя переменной с данными |
| result_variable_name | string | да | Куда сохранить выбор |
| display_text | string | нет | Текст над кнопками |
| valid_node_id | string | нет | Узел при валидном выборе |
| invalid_node_id | string | нет | Узел при невалидном выборе |

---

## 9. ExtendBlock — Переход в дочерний сценарий

Запускает другой сценарий с возможностью возврата.

```json
{
  "id": "extend_1",
  "type": "extend",
  "scenario_id": 2,
  "return_back": true
}
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| id | string | да | Уникальный ID блока |
| type | "extend" | да | Тип блока |
| scenario_id | number | да | ID целевого сценария |
| return_back | boolean | нет | Вернуться после завершения (default: false) |

---

## 10. MatchExtendBlock — Условный extend

Выбирает сценарий по правилам активации.

```json
{
  "id": "match_extend_1",
  "type": "match_extend",
  "scenario_ids": [2, 3, 4]
}
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| id | string | да | Уникальный ID блока |
| type | "match_extend" | да | Тип блока |
| scenario_ids | array[number] | да | Список ID возможных сценариев |

---

## 11. LLMBlock — Запрос к LLM

Отправляет запрос к языковой модели.

```json
{
  "id": "llm_1",
  "type": "llm",
  "result_variable_name": "llm_response",
  "system_message": "Ты полезный ассистент",
  "user_message": "Помоги с вопросом: {{session.question}}",
  "history_depth": 3,
  "model": {
    "url": "https://api.openai.com/v1",
    "model_name": "gpt-4",
    "token": "sk-...",
    "max_tokens": 500,
    "temperature": 0.7
  },
  "ok_target_node_id": "success",
  "error_target_node_id": "error"
}
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| id | string | да | Уникальный ID блока |
| type | "llm" | да | Тип блока |
| result_variable_name | string | да | Куда сохранить ответ |
| system_message | string | да | Системный промпт |
| user_message | string | да | Сообщение пользователя (Handlebars) |
| history_depth | number | нет | Сколько последних сообщений включить |
| model | object | да | Конфигурация модели |
| ok_target_node_id | string | нет | Узел при успехе |
| error_target_node_id | string | нет | Узел при ошибке |

**ModelConfig:**
| Поле | Тип | Описание |
|------|-----|----------|
| url | string | URL API |
| model_name | string | Имя модели |
| token | string | API ключ |
| max_tokens | number | Макс. токенов |
| temperature | number | Температура (0-1) |
| top_p | number | Top-p sampling |
| frequency_penalty | number | Штраф за частоту |
| presence_penalty | number | Штраф за присутствие |

---

## 12. AgentBlock — ReAct Agent с инструментами

Agent с возможностью вызова MCP tools.

```json
{
  "id": "agent_1",
  "type": "agent",
  "result_variable_name": "agent_result",
  "system_message": "Ты исследователь. Используй инструменты для поиска информации.",
  "user_message": "Найди: {{session.query}}",
  "history_depth": 5,
  "model": {
    "url": "https://api.openai.com/v1",
    "model_name": "gpt-4",
    "token": "sk-...",
    "max_tokens": 2000
  },
  "tools": {
    "mcp_servers": [
      {"url": "http://mcp-server:5000"}
    ]
  }
}
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| id | string | да | Уникальный ID блока |
| type | "agent" | да | Тип блока |
| result_variable_name | string | да | Куда сохранить результат |
| system_message | string | да | Системный промпт |
| user_message | string | да | Задача для агента |
| history_depth | number | нет | Глубина истории |
| model | object | да | Конфигурация модели |
| tools | object | нет | Конфигурация инструментов |

---

## 13. CloseBlock — Закрыть диалог

Завершает диалог и очищает состояние.

```json
{
  "id": "close_1",
  "type": "close"
}
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| id | string | да | Уникальный ID блока |
| type | "close" | да | Тип блока |

---

## 14. GoOperatorBlock — Переход к оператору

Специальный блок для передачи оператору.

```json
{
  "id": "go_operator_1",
  "type": "go_operator",
  "additional_metadata": {
    "reason": "user_request"
  }
}
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| id | string | да | Уникальный ID блока |
| type | "go_operator" | да | Тип блока |
| additional_metadata | object | нет | Дополнительные данные |

---

## Контекстные переменные (для Handlebars)

В любом текстовом поле можно использовать переменные:

```
{{system.last_user_message}}     — последнее сообщение пользователя
{{system.source_message}}        — оригинальное сообщение
{{system.current_scenario_id}}   — ID текущего сценария
{{system.utc_now_dt}}            — текущая дата/время

{{session.variable_name}}        — переменная сессии
{{request.variable_name}}        — переменная запроса
{{temp.variable_name}}           — временная переменная

{{nlu.matches}}                  — результаты regex matching
{{nlu.intents}}                  — результаты классификации
```
