# Troubleshooting: V2 нода не появляется

## Проблема
V2 нода регистрируется успешно в Python, но не появляется в ComfyUI UI.

## Решения

### 1. Полный перезапуск ComfyUI
```bash
# Закройте ComfyUI полностью
# Убедитесь что процесс завершен (Task Manager)
# Запустите заново
```

### 2. Очистите кэш Python
```bash
cd D:\AIGenerator\ComfyUI_NEW\ComfyUI_windows_portable\ComfyUI\custom_nodes\UniversalLLM
rm -rf __pycache__
```

### 3. Проверьте консоль ComfyUI
Должны быть эти строки:
```
[UniversalLLM V2] Loaded 4 presets from ...
[UniversalLLM V2] Async node registered successfully!
```

### 4. Поиск в UI
Попробуйте разные способы поиска:
- `Add Node` → `LLM` → ищите "V2"
- `Add Node` → поиск "Universal"
- `Add Node` → поиск "Async"
- Правый клик → `Add Node` → поиск "LLM"

### 5. Проверьте что нода точно загружена
В консоли ComfyUI при старте должно быть:
```
Loading: custom_nodes/UniversalLLM
[UniversalLLM V2] Async node registered successfully!
```

### 6. Если все равно не появляется - используйте V1
V1 работает, просто без async. Функциональность та же.

## Быстрый тест
Запустите этот скрипт:
```bash
cd D:\AIGenerator\ComfyUI_NEW\ComfyUI_windows_portable
.\python_embeded\python.exe -c "import sys; sys.path.insert(0, 'ComfyUI'); from custom_nodes.UniversalLLM import NODE_DISPLAY_NAME_MAPPINGS; print(NODE_DISPLAY_NAME_MAPPINGS)"
```

Должно вывести:
```python
{'UniversalLLMPromptNode': 'Universal LLM Prompt', 
 'UniversalLLMPromptNodeV2': 'Universal LLM Prompt V2 (Async)'}
```

## Альтернатива: Переименуйте V2 в V1
Если V2 не работает, можно заменить V1 на V2:
```bash
cd D:\AIGenerator\ComfyUI_NEW\ComfyUI_windows_portable\ComfyUI\custom_nodes\UniversalLLM
mv universal_llm_prompt_node.py universal_llm_prompt_node_old.py
mv universal_llm_prompt_node_v2.py universal_llm_prompt_node.py
```

Затем отредактируйте `universal_llm_prompt_node.py`:
- Переименуйте класс: `UniversalLLMPromptNodeV2` → `UniversalLLMPromptNode`
- Обновите `NODE_CLASS_MAPPINGS`
- Обновите `NODE_DISPLAY_NAME_MAPPINGS`

Тогда старая нода станет async версией!
