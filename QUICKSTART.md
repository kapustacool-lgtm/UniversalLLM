# Quick Start Guide - Universal LLM Prompt V2

## 🚀 Быстрый старт (30 секунд)

### 1. Перезапустите ComfyUI
Закройте и откройте ComfyUI заново, чтобы загрузить новую ноду.

### 2. Найдите ноду
В меню "Add Node" → "LLM" → **"Universal LLM Prompt V2 (Async)"**

### 3. Настройте
Минимальная конфигурация:
- **URL**: `https://api.deepseek.com/v1` (бесплатно!)
- **API Key**: Ваш ключ с platform.deepseek.com
- **Model**: `deepseek-chat`
- **Prompt**: Ваш текст

### 4. Запустите!
Нажмите "Queue Prompt" - UI не зависнет! 🎉

---

## 📋 Примеры конфигураций

### DeepSeek (бесплатно, рекомендуется)
```
URL: https://api.deepseek.com/v1
API Key: sk-xxxxxxxxxxxxxxxx
Model: deepseek-chat
Temperature: 0.7
Max Tokens: 1000
```

### Groq (бесплатно, очень быстро)
```
URL: https://api.groq.com/openai/v1
API Key: gsk_xxxxxxxxxxxxxxxx
Model: qwen2.5-72b-instruct
Temperature: 0.7
Max Tokens: 1000
```

### Local llama.cpp (приватно)
```
URL: http://127.0.0.1:8080
API Key: (оставить пустым)
Model: qwen2-vl:7b
Temperature: 0.7
Max Tokens: 1000
```

### OpenAI (платно)
```
URL: https://api.openai.com/v1
API Key: sk-xxxxxxxxxxxxxxxx
Model: gpt-4
Temperature: 0.7
Max Tokens: 1000
```

---

## 🎯 Основные фичи

### ✅ Async = UI не зависает
**V1:** UI мертв 120 секунд  
**V2:** UI работает всегда!

### ✅ Vision модели
Подключите изображение к входу `image` для vision моделей:
- qwen2-vl
- gpt-4-vision
- claude-3-opus

### ✅ System Prompts
Выберите пресет или используйте свой:
- Редактируйте `presets.json`
- Добавляйте свои промпты
- Переключайтесь на лету

### ✅ Smart Resize
Автоматический ресайз изображений:
- Включите `image_resize`
- Установите размер (1024x1024 по умолчанию)
- Оптимизация для API

---

## 🔧 Troubleshooting

### Нода не появляется?
1. Перезапустите ComfyUI
2. Проверьте консоль: должно быть `[UniversalLLM V2] Async node registered successfully!`
3. Если нет - проверьте `aiohttp`: `pip install aiohttp`

### API не отвечает?
1. Проверьте URL (без `/` в конце)
2. Проверьте API ключ
3. Проверьте модель (должна существовать)
4. Смотрите консоль для деталей

### Ошибка с изображением?
1. Убедитесь что модель поддерживает vision
2. Проверьте формат (PNG/JPEG)
3. Попробуйте включить resize

---

## 💡 Советы

### Для промптинга Flux
```
System Prompt: "You are an expert at creating detailed image prompts..."
Prompt: "a woman in a red dress..."
Temperature: 0.7
Max Tokens: 500
```

### Для оптимизации промптов
```
System Prompt: "Optimize this prompt for Flux Klein 9B..."
Prompt: [ваш исходный промпт]
Temperature: 0.5
Max Tokens: 1000
```

### Для vision анализа
```
Model: qwen2-vl:7b
Image: [подключите изображение]
Prompt: "Describe this image in detail"
Image Resize: true (1024x1024)
```

---

## 📊 V1 vs V2

| Что | V1 | V2 |
|-----|----|----|
| UI блокировка | ❌ Да | ✅ Нет |
| Async | ❌ | ✅ |
| Типизация | ⚠️ | ✅ |
| Функции | ✅ | ✅ |

**Вывод:** Используйте V2, V1 оставлен для совместимости.

---

## 🆘 Помощь

**Проблемы?**
1. Смотрите консоль ComfyUI
2. Читайте README.md
3. Проверьте CHANGELOG.md

**Работает?**
Наслаждайтесь async промптингом! 🚀

---

**Версия:** 2.0.0  
**Дата:** 2026-04-19
