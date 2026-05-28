# Universal LLM V3 - Quick Reference

## Что нового в V3?

**V3 = Smart Format Detection** 🎯

Автоматически выбирает правильный формат запроса (string vs multimodal) в зависимости от модели и наличия изображения.

---

## Ключевые отличия от V2

| Параметр | V2 | V3 |
|----------|----|----|
| Формат по умолчанию | Всегда multimodal | Smart (string или multimodal) |
| Новый параметр | - | `force_multimodal` |
| System messages | Всегда в массиве | Только когда нужно |
| LongCat API | Не работает | ✅ Работает |
| Производительность | Хорошая | Лучше (меньше overhead) |

---

## Когда включать force_multimodal?

### ✅ TRUE (включить):
- **LongCat-Flash-Omni-2603** - обязательно!
- Модели, которые явно требуют multimodal формат
- Когда получаете ошибку "json format error"

### ❌ FALSE (выключить):
- Все остальные модели (GPT, Claude, Llama, Mistral, etc.)
- Ollama локально
- Большинство OpenAI-совместимых API

### 🤖 AUTO (автоматически):
- Если подключено изображение → автоматически multimodal
- Если нет изображения и force_multimodal=FALSE → string format

---

## Быстрый старт

### 1. LongCat Omni
```
Node: Universal LLM Prompt V3 (Smart Format)
URL: https://api.longcat.chat/openai
API Key: ak_2Ka6vY3gR8Ub8NX69Y3jr5Tg2IH3m
Model: LongCat-Flash-Omni-2603
Force Multimodal: TRUE ← важно!
```

### 2. Ollama Local
```
Node: Universal LLM Prompt V3 (Smart Format)
URL: http://127.0.0.1:11434
API Key: (пусто)
Model: qwen2-vl:7b
Force Multimodal: FALSE
```

### 3. OpenAI
```
Node: Universal LLM Prompt V3 (Smart Format)
URL: https://api.openai.com/v1
API Key: sk-...
Model: gpt-4
Force Multimodal: FALSE
```

---

## Troubleshooting

### ❌ "json format error"
**Решение:** Включите `force_multimodal = TRUE`

### ❌ Модель не отвечает
**Проверьте:**
1. URL правильный?
2. API key правильный?
3. Модель доступна?

### ❌ Изображение не работает
**Проверьте:**
1. Модель поддерживает vision?
2. Изображение подключено к входу `image`?
3. `force_multimodal` можно оставить FALSE (включится автоматически)

---

## Формат запросов (под капотом)

### String Format (force_multimodal=FALSE, без изображения)
```json
{
  "messages": [
    {"role": "system", "content": "You are..."},
    {"role": "user", "content": "Generate prompt"}
  ]
}
```

### Multimodal Format (force_multimodal=TRUE или с изображением)
```json
{
  "messages": [
    {
      "role": "system",
      "content": [{"type": "text", "text": "You are..."}]
    },
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "Generate prompt"},
        {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}
      ]
    }
  ]
}
```

---

## Миграция с V2

1. Замените ноду V2 на V3
2. Добавьте параметр `force_multimodal`:
   - LongCat Omni → TRUE
   - Все остальные → FALSE
3. Готово!

**Совместимость:** V3 полностью обратно совместима с V2 workflows.

---

## Дата обновления

**2026-05-11** - V3 Release
