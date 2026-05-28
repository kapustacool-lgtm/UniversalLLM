# Universal LLM Prompt Node for ComfyUI

Универсальная нода для генерации промптов через LLM API с поддержкой различных форматов и провайдеров.

## Версии

### V3 - Smart Format ⭐ (RECOMMENDED)
**Новая версия с умным определением формата!**

- ✅ **Smart format detection** - автоматически выбирает формат (string vs multimodal)
- ✅ **Force multimodal** - опция для принудительного использования мультимодального формата
- ✅ **Оптимизированная обработка** - system messages не оборачиваются в массив без необходимости
- ✅ **Поддержка LongCat API** - правильная обработка `/openai` endpoint
- ✅ **Async/Await** - неблокирующие API вызовы
- ✅ **Улучшенная обработка ошибок**

### V2 - Async (Deprecated)
Асинхронная версия с мультимодальным форматом для всех запросов.

**Проблема:** Всегда использует мультимодальный формат, даже когда модель его не требует.

### V1 - Original (Legacy)
Базовая версия с синхронными запросами.

---

## Когда использовать какой формат

### String Format (по умолчанию в V3)
Используется для большинства моделей:
```json
{
  "role": "user",
  "content": "Your text here"
}
```

**Подходит для:**
- OpenAI GPT-4, GPT-3.5
- Anthropic Claude
- Mistral, Llama
- Большинство локальных моделей через Ollama

### Multimodal Format (force_multimodal=True)
Используется для мультимодальных моделей:
```json
{
  "role": "user",
  "content": [
    {"type": "text", "text": "Your text here"}
  ]
}
```

**Обязателен для:**
- ✅ **LongCat-Flash-Omni-2603** (даже без изображений!)
- ✅ Vision models с изображениями
- ✅ Модели, требующие структурированный input

---

## Примеры использования V3

### Пример 1: LongCat Omni (требует multimodal)

```
URL: https://api.longcat.chat/openai
API Key: ak_2Ka6vY3gR8Ub8NX69Y3jr5Tg2IH3m
Model: LongCat-Flash-Omni-2603
Force Multimodal: ✅ TRUE (обязательно!)
```

### Пример 2: Ollama локально (string format)

```
URL: http://127.0.0.1:11434
API Key: (пусто)
Model: qwen2-vl:7b
Force Multimodal: ❌ FALSE
```

### Пример 3: OpenAI API (string format)

```
URL: https://api.openai.com/v1
API Key: sk-...
Model: gpt-4
Force Multimodal: ❌ FALSE
```

### Пример 4: Vision model с изображением (auto multimodal)

```
URL: http://127.0.0.1:11434
Model: llava:13b
Image: (подключить изображение)
Force Multimodal: ❌ FALSE (автоматически включится)
```

---

## Параметры ноды V3

### Обязательные:
- **prompt** - текст запроса к модели
- **system_prompt_preset** - выбор пресета из presets.json
- **system_prompt_custom** - кастомный system prompt (если preset = "Empty")
- **url** - URL API endpoint
- **api_key** - API ключ (может быть пустым для локальных моделей)
- **model** - название модели
- **temperature** - температура генерации (0.0-2.0)
- **max_tokens** - максимум токенов в ответе

### Новые в V3:
- **force_multimodal** - принудительно использовать мультимодальный формат
  - `FALSE` (default) - автоматический выбор формата
  - `TRUE` - всегда использовать multimodal (для LongCat Omni)

### Опциональные:
- **image** - входное изображение (автоматически включает multimodal)
- **image_resize** - изменять размер изображения
- **resize_width** - ширина (default: 1024)
- **resize_height** - высота (default: 1024)

---

## Поддерживаемые API

### Локальные:
- ✅ Ollama (http://localhost:11434)
- ✅ llama.cpp server
- ✅ LocalAI
- ✅ text-generation-webui

### Облачные:
- ✅ OpenAI API
- ✅ Anthropic Claude API
- ✅ **LongCat API** (https://api.longcat.chat/openai) - требует force_multimodal!
- ✅ OpenRouter
- ✅ Together AI
- ✅ Groq
- ✅ DeepSeek
- ✅ Любой OpenAI-совместимый API

---

## System Prompts

Edit `presets.json` to add your own system prompts:

```json
{
  "presets": {
    "My Custom Preset": "Your system prompt here...",
    "Another Preset": "Another prompt..."
  }
}
```

---

## Troubleshooting

### Ошибка: "json format error"
**Причина:** Модель требует мультимодальный формат, но получает string.

**Решение:** Включите `force_multimodal = TRUE`

**Пример:** LongCat-Flash-Omni-2603 всегда требует multimodal формат.

### Ошибка: "API Error 400"
**Причина:** Неправильный формат запроса или недоступная модель.

**Решение:** 
1. Проверьте название модели
2. Проверьте URL endpoint
3. Попробуйте переключить `force_multimodal`

### Ошибка: "Request timeout"
**Причина:** Модель слишком долго генерирует ответ (>120s).

**Решение:** Уменьшите `max_tokens` или используйте более быструю модель.

### Node doesn't appear
- Restart ComfyUI
- Check console for errors
- Verify `aiohttp` is installed

### Image not working
- Ensure model supports vision (e.g., qwen2-vl, gpt-4-vision)
- Check image format (PNG/JPEG)
- Try resizing image

---

## Changelog

### V3 (2026-05-11) ⭐ NEW
- ✅ Добавлен параметр `force_multimodal`
- ✅ Smart format detection (автоматический выбор string/multimodal)
- ✅ Оптимизирована обработка LongCat API endpoint
- ✅ Улучшена обработка endpoint URL (поддержка `/openai` пути)
- ✅ Исправлена избыточная обертка system messages в массив
- ✅ Оптимизирована функция `format_messages_smart()`

### V2 (Previous)
- ✅ Async/await для неблокирующих запросов
- ✅ Мультимодальный формат для всех запросов
- ✅ Поддержка streaming responses
- ⚠️ Проблема: всегда использует multimodal, даже когда не нужно

### V1 (Original)
- ✅ Базовая функциональность
- ✅ Синхронные запросы
- ✅ Поддержка presets

---

## Migration Guide

### From V2 to V3:
1. Замените ноду "Universal LLM Prompt V2" на "Universal LLM Prompt V3"
2. Если используете LongCat Omni: включите `force_multimodal = TRUE`
3. Для остальных моделей: оставьте `force_multimodal = FALSE`
4. Готово!

### From V1 to V3:
1. Замените ноду "Universal LLM Prompt" на "Universal LLM Prompt V3"
2. Переподключите входы
3. Настройте `force_multimodal` если нужно
4. Готово!

---

## License

MIT License - Free to use and modify

## Author

Created for ComfyUI community
Updated: 2026-05-11 (V3 release)
