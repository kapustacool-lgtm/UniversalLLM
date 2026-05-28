# Universal LLM Prompt Node for ComfyUI

Connect any OpenAI-compatible LLM (local or cloud) to generate, enhance, and refine prompts — or perform image analysis, Q&A, and any LLM task — directly inside ComfyUI.

## Features

### Dual Model Architecture (Vision → Text)
1. **Vision model** analyzes an image (e.g., "Describe this scene")
2. **Text model** uses that analysis + your prompt to generate the final result

### Single Mode (Multimodal)
One multimodal model handles both image and text in a single pass — ideal for vision-capable models like `qwen2-vl`, `llava`, `gpt-4-vision`.

### Smart Format Detection (V3)
Automatically selects the correct message format:
- **String** — for most models (GPT, Claude, Mistral, Llama...)
- **Multimodal array** — for vision models and APIs like LongCat Omni

### Universal API Support
Any OpenAI-compatible endpoint:
- **Local:** Ollama, llama.cpp, LocalAI, text-generation-webui
- **Cloud:** OpenAI, Anthropic Claude, LongCat, OpenRouter, Groq, DeepSeek, Together AI

### System Prompt Presets
Built-in presets for popular workflows:
- **LTX Video 2.3 I2V** — Russian-to-English motion description converter for video generation
- **Flux Klein 9B** — overspecified prompts compensating for model weaknesses
- **Flux Photo / SDXL** — natural language and booru-style prompt generators
- Add your own via `presets.json`

## Nodes Included

| Node | Description |
|------|-------------|
| **ComfyUI Dual VLLM (V5)** | Latest — Dual/Single Mode, synchronous, clean status outputs |
| **Universal LLM Prompt V4** | Same dual architecture, slightly older interface |
| **Universal LLM Prompt V3** | Smart format detection, async support ⭐ RECOMMENDED |
| **Universal LLM Prompt V2** | Async (deprecated) |
| **Universal LLM Prompt V1** | Original sync version (legacy) |

## Installation

### Via Git (recommended)
Open a terminal in your ComfyUI directory and run:
```bash
cd custom_nodes
git clone https://github.com/YOUR_USERNAME/ComfyUI-UniversalLLM.git
cd ComfyUI-UniversalLLM
pip install -r requirements.txt
```
Then **restart ComfyUI**.

### Manual
1. Download or copy this folder to `ComfyUI/custom_nodes/UniversalLLM`
2. Install dependencies:
   ```bash
   cd ComfyUI/custom_nodes/UniversalLLM
   pip install -r requirements.txt
   ```
3. Restart ComfyUI

After restart, find the nodes in the **LLM** category.

## Quick Start

1. Add the node **ComfyUI Dual VLLM** to your workflow
2. Set your API endpoint (e.g., `http://127.0.0.1:11434` for Ollama)
3. Enter a model name (e.g., `qwen2:7b`)
4. Type your prompt and run
5. The generated prompt appears at the `generated_prompt` output

## Parameters (V5 / V4)

### Required
- **prompt** — your query to the LLM
- **system_prompt_preset** — select a preset from `presets.json`
- **system_prompt_custom** — custom system prompt (if preset = "Empty")
- **vision/url, vision/api_key, vision/model** — vision model connection
- **text/url, text/api_key, text/model** — text model connection
- **temperature** — generation temperature (0.0–2.0)
- **max_tokens** — max tokens in response

### Optional
- **image** — input image (automatically enables multimodal mode)
- **image_resize** — resize image before sending
- **resize_width/height** — target dimensions (default: 1024)
- **image_format** — JPEG / PNG / WEBP
- **image_quality** — compression quality (10–100)
- **vision_prompt** — custom prompt for the vision model

## System Prompts

Edit `presets.json` to add your own presets:

```json
{
  "presets": {
    "My Custom Preset": "Your system prompt here...",
    "Another Preset": "Another prompt..."
  }
}
```

## Changelog

### V5 — ComfyUI Dual VLLM (Latest)
- Dual model architecture (Vision → Text pipeline)
- Single Mode (multimodal) for vision-capable models
- Clean status outputs for debugging

### V4 — Universal LLM Prompt V4
- Same dual architecture as V5
- Russian locale system format options

### V3 — Smart Format (2026-05-11) ⭐
- `force_multimodal` parameter added
- Smart format detection (auto string/multimodal)
- Optimized LongCat API handling
- Fixed redundant system message wrapping

### V2 — Async (Previous)
- Async/await for non-blocking requests
- Always used multimodal format (problematic)

### V1 — Original
- Basic sync functionality
- Preset support

## License

MIT — Free to use and modify

## Author

Created for the ComfyUI community