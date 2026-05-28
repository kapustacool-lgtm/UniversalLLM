# Universal LLM Node - Version Comparison & Analysis

## 📊 Сравнительная таблица версий

| Функция | V1 | V2 | V3 | V4 | V5 |
|---------|----|----|-----|-----|-----|
| **Async/Await** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Формат запросов** | String | Всегда Multimodal | Smart (Auto) | Smart (Auto) | Smart (Auto) |
| **force_multimodal параметр** | ❌ | ❌ | ✅ | ✅ | ✅ |
| **LongCat Omni поддержка** | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Оптимизация system messages** | N/A | ❌ | ✅ | ✅ | ✅ |
| **Streaming support** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Image support** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Dual Mode (Vision + Text)** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Memory cache** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **System prompt cache** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Производительность** | Средняя | Хорошая | Отличная | Отличная | Отличная |
| **Статус** | Legacy | Deprecated | Deprecated | Deprecated | **Recommended** |

---

## 🔍 Детальный анализ

### V1 - Original (Legacy)
**Файл:** `universal_llm_prompt_node.py`

**Плюсы:**
- ✅ Простая реализация
- ✅ Стабильная работа
- ✅ Совместимость со старыми workflows

**Минусы:**
- ❌ Синхронные запросы (блокирует UI)
- ❌ Нет поддержки multimodal формата
- ❌ Устаревший код

**Когда использовать:**
- Только для совместимости со старыми workflows
- Не рекомендуется для новых проектов

---

### V2 - Async (Deprecated)
**Файл:** `universal_llm_prompt_node_v2.py`

**Плюсы:**
- ✅ Async/await (не блокирует UI)
- ✅ Поддержка streaming
- ✅ Multimodal формат
- ✅ Современный код

**Минусы:**
- ❌ **Всегда использует multimodal формат** (даже когда не нужно)
- ❌ Избыточная обертка system messages в массив
- ❌ Не работает с LongCat Omni через Omniroute
- ❌ Нет опции выбора формата

**Проблема:**
```python
# V2 всегда делает так:
{"role": "system", "content": [{"type": "text", "text": "..."}]}

# Даже когда модель ожидает:
{"role": "system", "content": "..."}
```

**Когда использовать:**
- Не рекомендуется (используйте V3)
- Только если V3 по какой-то причине не работает

---

### V3 - Smart Format ⭐ (Deprecated)
**Файл:** `universal_llm_prompt_node_v3.py`

**Плюсы:**
- ✅ **Smart format detection** - автоматически выбирает правильный формат
- ✅ **force_multimodal параметр** - ручное управление форматом
- ✅ Async/await (не блокирует UI)
- ✅ Поддержка streaming
- ✅ Оптимизированная обработка messages
- ✅ **Работает с LongCat Omni** (через прямой API)
- ✅ Улучшенная обработка endpoint URL
- ✅ Лучшая производительность

**Новые возможности:**
```python
def format_messages_smart(
    messages: list,
    image_base64: Optional[str] = None,
    force_multimodal: bool = False
) -> list:
    """
    Smart formatting:
    - force_multimodal=False + no image → string format
    - force_multimodal=True OR image → multimodal format
    """
```

**Когда использовать:**
- ⚠️ Только для обратной совместимости
- ⚠️ Если V5 по какой-то причине не работает

---

## 🎯 Рекомендации по использованию

### Для новых проектов:
**Используйте V5** - это самая современная версия с Dual Model архитектурой.

### Для существующих workflows:
- **V1/V2 workflows** → Мигрируйте на V5
- **V3/V4 workflows** → Мигрируйте на V5 (рекомендуется)

### Для работы с изображениями:
**V5** с Dual Mode (Vision + Text) или Single Mode

### Для текста без изображений:
**V5** в Single Mode

---

## 🔧 Технические детали

### Обработка endpoint URL

**V2:**
```python
if url.endswith('/v1') or url.endswith('/v1/'):
    endpoint = f"{url.rstrip('/')}/chat/completions"
elif is_local_url(url):
    endpoint = f"{url}/v1/chat/completions"
else:
    endpoint = f"{url}/chat/completions"
```

**V3 (улучшено):**
```python
if url.endswith('/v1') or url.endswith('/v1/'):
    endpoint = f"{url.rstrip('/')}/chat/completions"
elif '/openai' in url:
    # LongCat API: https://api.longcat.chat/openai
    if not url.endswith('/v1/chat/completions'):
        endpoint = f"{url.rstrip('/')}/v1/chat/completions"
    else:
        endpoint = url
elif is_local_url(url):
    endpoint = f"{url}/v1/chat/completions"
else:
    endpoint = f"{url}/chat/completions"
```

### Форматирование messages

**V2 (всегда multimodal):**
```python
# System message
formatted_messages.append({
    "role": "system",
    "content": [{"type": "text", "text": msg["content"]}]
})

# User message
formatted_messages.append({
    "role": "user",
    "content": [{"type": "text", "text": msg["content"]}]
})
```

**V3 (smart):**
```python
if use_multimodal:
    # Multimodal format
    formatted_messages.append({
        "role": role,
        "content": [{"type": "text", "text": content}]
    })
else:
    # Simple string format
    formatted_messages.append({
        "role": role,
        "content": content
    })
```

---

## 📈 Производительность

### Overhead на запрос:

| Версия | String format | Multimodal format |
|--------|---------------|-------------------|
| V1 | ✅ Минимальный | ❌ Не поддерживается |
| V2 | ❌ Всегда multimodal | ✅ Средний |
| V3 | ✅ Минимальный | ✅ Минимальный |

### Размер payload:

**String format:**
```json
{"role": "user", "content": "text"}  // ~35 bytes
```

**Multimodal format:**
```json
{"role": "user", "content": [{"type": "text", "text": "text"}]}  // ~60 bytes
```

**Экономия:** ~40% меньше данных при использовании string format (V3 auto)

---

## 🐛 Известные проблемы

### V1:
- Блокирует UI во время запросов
- Нет поддержки современных multimodal моделей

### V2:
- Не работает с некоторыми API (LongCat Omni через Omniroute)
- Избыточный overhead для простых моделей
- Нет возможности выбрать формат

### V3:
- Нет известных проблем ✅

---

## 📝 Changelog Summary

### 2026-05-11 - V3 Release
- ✅ Добавлен smart format detection
- ✅ Добавлен параметр force_multimodal
- ✅ Исправлена поддержка LongCat API
- ✅ Оптимизирована обработка messages
- ✅ Улучшена обработка endpoint URL

### 2024-04-19 - V2 Release
- ✅ Async/await implementation
- ✅ Multimodal format support
- ✅ Streaming support
- ⚠️ Всегда использует multimodal (проблема)

### Original - V1 Release
- ✅ Базовая функциональность
- ✅ Sync implementation

---

## 🎓 Выводы

**V5 - актуальная версия с Dual Model архитектурой:**

1. **Dual Mode (Vision + Text)** — два отдельных API вызова
2. **Single Mode (Multimodal Text)** — одна модель для всего
3. **Кэширование system prompt** — экономия токенов
4. **Smart endpoint construction** — корректная работа с любыми API
5. **Streaming support** — поддержка потоковых ответов

**Рекомендация:** Используйте V5 для всех новых и существующих проектов.

---

**Дата анализа:** 2026-05-28
**Версия документа:** 2.0

---

## 🔄 V5 — Актуальная версия

**Файл:** `universal_llm_prompt_node_v5.py`

V5 — прямой преемник V4. Обновление версии отражает стабилизацию архитектуры Dual Model (Vision + Text).

**Рекомендация:** Используйте V5 для всех новых проектов. V4 остаётся для обратной совместимости с существующими workflows.
