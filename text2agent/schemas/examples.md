# Agent Examples

Примеры готовых агентов для разных use cases.

---

## 1. Simple FAQ Bot

FAQ бот с несколькими вопросами и ответами.

```json
{
  "bot_name": "FAQ Bot",
  "author": "text2agent",
  "request_ttl_in_seconds": 30,
  "no_match_stub_answer": "Извините, я не знаю ответа на этот вопрос",
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
            {"id": "w1", "type": "answer", "value": "Привет! Я FAQ бот. Спросите меня о часах работы, доставке или оплате."},
            {"id": "w2", "type": "wait_for_user"}
          ]
        },
        {
          "id": "fallback",
          "blocks": [
            {"id": "f1", "type": "answer", "value": "Не нашёл ответа. Попробуйте спросить о часах работы, доставке или оплате."}
          ]
        }
      ]
    },
    {
      "name": "hours",
      "slug": "hours",
      "entry_edges": [
        {"type": "match", "value": "час.*работ|режим|график|открыт", "target_node_id": "hours_answer"}
      ],
      "nodes": [
        {
          "id": "hours_answer",
          "blocks": [
            {"id": "h1", "type": "answer", "value": "Мы работаем с 9:00 до 18:00, понедельник-пятница."}
          ]
        }
      ]
    },
    {
      "name": "delivery",
      "slug": "delivery",
      "entry_edges": [
        {"type": "match", "value": "доставк|привез|курьер|получить", "target_node_id": "delivery_answer"}
      ],
      "nodes": [
        {
          "id": "delivery_answer",
          "blocks": [
            {"id": "d1", "type": "answer", "value": "Доставка осуществляется в течение 1-3 рабочих дней. Стоимость: 300 руб."}
          ]
        }
      ]
    },
    {
      "name": "payment",
      "slug": "payment",
      "entry_edges": [
        {"type": "match", "value": "оплат|заплатить|карт|наличн", "target_node_id": "payment_answer"}
      ],
      "nodes": [
        {
          "id": "payment_answer",
          "blocks": [
            {"id": "p1", "type": "answer", "value": "Принимаем оплату картой, наличными при получении и через СБП."}
          ]
        }
      ]
    }
  ]
}
```

---

## 2. Lead Generation Bot

Бот для сбора контактных данных.

```json
{
  "bot_name": "Lead Bot",
  "author": "text2agent",
  "request_ttl_in_seconds": 60,
  "no_match_stub_answer": "Пожалуйста, ответьте на вопрос",
  "need_preprocess": "disabled",
  "scenarios": [
    {
      "name": "main",
      "slug": "main",
      "entry_edges": [
        {"type": "event", "value": "init", "target_node_id": "welcome"}
      ],
      "nodes": [
        {
          "id": "welcome",
          "blocks": [
            {"id": "w1", "type": "answer", "value": "Здравствуйте! Оставьте заявку и мы свяжемся с вами."},
            {"id": "w2", "type": "answer", "value": "Как вас зовут?"},
            {"id": "w3", "type": "wait_for_user"}
          ],
          "next_node_id": "get_name"
        },
        {
          "id": "get_name",
          "blocks": [
            {
              "id": "save_name",
              "type": "variables",
              "name": "user_name",
              "value": "context.system.last_user_message",
              "variable_type": "python"
            },
            {"id": "ask_phone", "type": "answer", "value": "Приятно познакомиться, {{session.user_name}}! Укажите ваш телефон:"},
            {"id": "wait_phone", "type": "wait_for_user"}
          ],
          "next_node_id": "get_phone"
        },
        {
          "id": "get_phone",
          "blocks": [
            {
              "id": "save_phone",
              "type": "variables",
              "name": "user_phone",
              "value": "context.system.last_user_message",
              "variable_type": "python"
            },
            {"id": "ask_email", "type": "answer", "value": "Отлично! И ваш email:"},
            {"id": "wait_email", "type": "wait_for_user"}
          ],
          "next_node_id": "get_email"
        },
        {
          "id": "get_email",
          "blocks": [
            {
              "id": "save_email",
              "type": "variables",
              "name": "user_email",
              "value": "context.system.last_user_message",
              "variable_type": "python"
            },
            {
              "id": "confirm",
              "type": "answer",
              "value": "Спасибо! Ваша заявка:\n\nИмя: {{session.user_name}}\nТелефон: {{session.user_phone}}\nEmail: {{session.user_email}}\n\nМы свяжемся с вами в ближайшее время!"
            },
            {"id": "close", "type": "close"}
          ]
        }
      ]
    }
  ]
}
```

---

## 3. Support Bot with Buttons

Бот поддержки с кнопками выбора.

```json
{
  "bot_name": "Support Bot",
  "author": "text2agent",
  "request_ttl_in_seconds": 60,
  "no_match_stub_answer": "Выберите тему из меню",
  "need_preprocess": "disabled",
  "scenarios": [
    {
      "name": "main",
      "slug": "main",
      "entry_edges": [
        {"type": "event", "value": "init", "target_node_id": "menu"},
        {"type": "event", "value": "no_match", "target_node_id": "menu"}
      ],
      "nodes": [
        {
          "id": "menu",
          "blocks": [
            {"id": "m1", "type": "answer", "value": "Выберите тему обращения:"},
            {
              "id": "m2",
              "type": "buttons",
              "buttons": [
                {"title": "Проблема с заказом", "target_node_id": "order_issue"},
                {"title": "Возврат товара", "target_node_id": "return"},
                {"title": "Связаться с оператором", "target_node_id": "operator"}
              ]
            }
          ]
        },
        {
          "id": "order_issue",
          "blocks": [
            {"id": "o1", "type": "answer", "value": "Опишите проблему с заказом:"},
            {"id": "o2", "type": "wait_for_user"}
          ],
          "next_node_id": "issue_received"
        },
        {
          "id": "return",
          "blocks": [
            {"id": "r1", "type": "answer", "value": "Для возврата товара:\n1. Заполните форму на сайте\n2. Отправьте товар в оригинальной упаковке\n3. Деньги вернутся в течение 5 дней"}
          ],
          "next_node_id": "menu"
        },
        {
          "id": "operator",
          "blocks": [
            {"id": "op1", "type": "answer", "value": "Переключаю на оператора..."},
            {"id": "op2", "type": "go_operator", "additional_metadata": {"reason": "user_request"}}
          ]
        },
        {
          "id": "issue_received",
          "blocks": [
            {
              "id": "ir1",
              "type": "variables",
              "name": "issue_description",
              "value": "context.system.last_user_message",
              "variable_type": "python"
            },
            {"id": "ir2", "type": "answer", "value": "Спасибо! Ваше обращение зарегистрировано. Мы ответим в течение 24 часов."}
          ]
        }
      ]
    }
  ]
}
```

---

## 4. LLM-Powered Assistant

Ассистент с интеграцией LLM.

```json
{
  "bot_name": "AI Assistant",
  "author": "text2agent",
  "request_ttl_in_seconds": 120,
  "no_match_stub_answer": "Произошла ошибка, попробуйте ещё раз",
  "need_preprocess": "disabled",
  "scenarios": [
    {
      "name": "main",
      "slug": "main",
      "entry_edges": [
        {"type": "event", "value": "init", "target_node_id": "welcome"},
        {"type": "match", "value": ".*", "target_node_id": "process_question"}
      ],
      "nodes": [
        {
          "id": "welcome",
          "blocks": [
            {"id": "w1", "type": "answer", "value": "Привет! Я AI ассистент. Задайте мне любой вопрос."},
            {"id": "w2", "type": "wait_for_user"}
          ],
          "next_node_id": "process_question"
        },
        {
          "id": "process_question",
          "blocks": [
            {
              "id": "llm1",
              "type": "llm",
              "result_variable_name": "ai_response",
              "system_message": "Ты полезный ассистент. Отвечай кратко и по делу на русском языке.",
              "user_message": "{{system.last_user_message}}",
              "history_depth": 5,
              "model": {
                "url": "https://api.openai.com/v1",
                "model_name": "gpt-4",
                "token": "${OPENAI_API_KEY}",
                "max_tokens": 500,
                "temperature": 0.7
              },
              "ok_target_node_id": "show_response",
              "error_target_node_id": "error_response"
            }
          ]
        },
        {
          "id": "show_response",
          "blocks": [
            {"id": "sr1", "type": "answer", "value": "{{session.ai_response}}"},
            {"id": "sr2", "type": "wait_for_user"}
          ],
          "next_node_id": "process_question"
        },
        {
          "id": "error_response",
          "blocks": [
            {"id": "er1", "type": "answer", "value": "Извините, произошла ошибка. Попробуйте переформулировать вопрос."},
            {"id": "er2", "type": "wait_for_user"}
          ],
          "next_node_id": "process_question"
        }
      ]
    }
  ]
}
```

---

## 5. Booking Bot with HTTP Integration

Бот бронирования с интеграцией через HTTP.

```json
{
  "bot_name": "Booking Bot",
  "author": "text2agent",
  "request_ttl_in_seconds": 60,
  "no_match_stub_answer": "Пожалуйста, следуйте инструкциям",
  "need_preprocess": "disabled",
  "scenarios": [
    {
      "name": "main",
      "slug": "main",
      "entry_edges": [
        {"type": "event", "value": "init", "target_node_id": "start"},
        {"type": "match", "value": "забронировать|бронь|записаться", "target_node_id": "start"}
      ],
      "nodes": [
        {
          "id": "start",
          "blocks": [
            {"id": "s1", "type": "answer", "value": "Давайте забронируем! На какую дату? (формат: ДД.ММ.ГГГГ)"},
            {"id": "s2", "type": "wait_for_user"}
          ],
          "next_node_id": "get_date"
        },
        {
          "id": "get_date",
          "blocks": [
            {
              "id": "gd1",
              "type": "variables",
              "name": "booking_date",
              "value": "context.system.last_user_message",
              "variable_type": "python"
            },
            {"id": "gd2", "type": "answer", "value": "На какое время? (например: 14:00)"},
            {"id": "gd3", "type": "wait_for_user"}
          ],
          "next_node_id": "get_time"
        },
        {
          "id": "get_time",
          "blocks": [
            {
              "id": "gt1",
              "type": "variables",
              "name": "booking_time",
              "value": "context.system.last_user_message",
              "variable_type": "python"
            },
            {"id": "gt2", "type": "answer", "value": "Проверяю доступность..."},
            {
              "id": "gt3",
              "type": "http_request",
              "url": "https://api.example.com/bookings/check",
              "method": "POST",
              "headers": [
                {"key": "Content-Type", "value": "application/json"}
              ],
              "body": "{\"date\": \"{{session.booking_date}}\", \"time\": \"{{session.booking_time}}\"}",
              "response_mapping": [
                {"key": "is_available", "value": "$.available", "map_to_single_value": true},
                {"key": "slot_id", "value": "$.slot_id", "map_to_single_value": true}
              ],
              "ok_target_node_id": "check_availability",
              "error_target_node_id": "api_error"
            }
          ]
        },
        {
          "id": "check_availability",
          "blocks": [
            {
              "id": "ca1",
              "type": "single_if",
              "expression": "session.get('is_available') == True",
              "code_type": "python",
              "target_node_id": "confirm_booking"
            }
          ],
          "next_node_id": "not_available"
        },
        {
          "id": "confirm_booking",
          "blocks": [
            {"id": "cb1", "type": "answer", "value": "Слот доступен! Бронирую на {{session.booking_date}} в {{session.booking_time}}..."},
            {
              "id": "cb2",
              "type": "http_request",
              "url": "https://api.example.com/bookings/create",
              "method": "POST",
              "body": "{\"slot_id\": \"{{session.slot_id}}\"}",
              "response_mapping": [
                {"key": "booking_id", "value": "$.id", "map_to_single_value": true}
              ],
              "ok_target_node_id": "success",
              "error_target_node_id": "api_error"
            }
          ]
        },
        {
          "id": "success",
          "blocks": [
            {"id": "su1", "type": "answer", "value": "Готово! Ваша бронь #{{session.booking_id}} на {{session.booking_date}} в {{session.booking_time}}."},
            {"id": "su2", "type": "close"}
          ]
        },
        {
          "id": "not_available",
          "blocks": [
            {"id": "na1", "type": "answer", "value": "К сожалению, это время занято. Выберите другое:"},
            {"id": "na2", "type": "wait_for_user"}
          ],
          "next_node_id": "get_time"
        },
        {
          "id": "api_error",
          "blocks": [
            {"id": "ae1", "type": "answer", "value": "Произошла ошибка. Попробуйте позже или обратитесь к оператору."},
            {"id": "ae2", "type": "go_operator"}
          ]
        }
      ]
    }
  ]
}
```

---

## Советы по проектированию

1. **Начинайте с main сценария** — он должен обрабатывать `init` и `no_match`
2. **Используйте уникальные slug** — они должны быть уникальными в рамках всего бота
3. **Добавляйте WaitForUserBlock** — когда ожидаете ввод от пользователя
4. **Сохраняйте данные в session** — для использования между узлами
5. **Предусматривайте fallback** — на случай ошибок и непонятных запросов
6. **Используйте кнопки** — для структурированного ввода
