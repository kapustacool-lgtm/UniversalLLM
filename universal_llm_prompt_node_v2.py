"""
Universal LLM Prompt Generator Node for ComfyUI (Modern Async Version)
======================================================================
Modern implementation with:
- ComfyNodeABC for better typing
- Async/await for non-blocking API calls
- Improved error handling
- Progress feedback
"""

import json
import aiohttp
import asyncio
import base64
import io as python_io
from PIL import Image
import torch
from torchvision.transforms import ToPILImage
import os
from typing import Optional, Tuple

from comfy.comfy_types import ComfyNodeABC, IO, InputTypeDict


# ══════════════════════════════════════════════════════════════════════════
# LOAD PRESETS FROM JSON
# ══════════════════════════════════════════════════════════════════════════
def load_presets():
    """Load system prompt presets from presets.json"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    presets_path = os.path.join(script_dir, "presets.json")

    if not os.path.exists(presets_path):
        presets_path = r"C:\scripts\presets.json"

    try:
        with open(presets_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            presets = data.get("presets", {})
            print(f"[UniversalLLM V2] Loaded {len(presets)} presets from {presets_path}")
            return presets
    except Exception as e:
        print(f"[UniversalLLM V2] Error loading presets: {e}")
        return {"Empty (use your own)": ""}

SYSTEM_PROMPTS = load_presets()


# ══════════════════════════════════════════════════════════════════════════
# IMAGE PROCESSING
# ══════════════════════════════════════════════════════════════════════════
def resize_image_smart(pil_image: Image.Image, target_width: int = 1024, target_height: int = 1024) -> Image.Image:
    """Resize image to exact target dimensions"""
    width, height = pil_image.size

    if width == target_width and height == target_height:
        print(f"[UniversalLLM V2] Image already at target size: {width}x{height}")
        return pil_image

    print(f"[UniversalLLM V2] Resizing image: {width}x{height} → {target_width}x{target_height}")
    return pil_image.resize((target_width, target_height), Image.Resampling.LANCZOS)


def tensor_to_pil(image_tensor) -> Image.Image:
    """Convert ComfyUI image tensor to PIL Image"""
    if isinstance(image_tensor, torch.Tensor):
        if image_tensor.dim() == 4:
            image_tensor = image_tensor.squeeze(0)
        if image_tensor.dim() != 3:
            raise ValueError(f"Expected 3D tensor, got {image_tensor.dim()}D")

        if image_tensor.shape[-1] in [1, 3, 4]:
            image_tensor = image_tensor.permute(2, 0, 1)

        pil_image = ToPILImage()(image_tensor)
        return pil_image
    elif isinstance(image_tensor, Image.Image):
        return image_tensor
    else:
        raise ValueError(f"Unsupported image type: {type(image_tensor)}")


def pil_to_base64(pil_image: Image.Image) -> str:
    """Convert PIL Image to base64 string"""
    buffered = python_io.BytesIO()
    pil_image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


# ══════════════════════════════════════════════════════════════════════════
# ASYNC API COMMUNICATION
# ══════════════════════════════════════════════════════════════════════════
def is_local_url(url: str) -> bool:
    """Check if URL is localhost"""
    return "localhost" in url.lower() or "127.0.0.1" in url


async def call_llm_api_async(
    url: str,
    api_key: str,
    model: str,
    messages: list,
    temperature: float,
    max_tokens: int,
    image_base64: Optional[str] = None
) -> Tuple[Optional[str], Optional[str]]:
    """Universal async LLM API caller"""
    headers = {"Content-Type": "application/json"}

    if api_key and api_key.strip():
        headers["Authorization"] = f"Bearer {api_key}"

    formatted_messages = []
    for msg in messages:
        if msg["role"] == "system":
            formatted_messages.append({
                "role": "system",
                "content": [{"type": "text", "text": msg["content"]}]
            })
        elif msg["role"] == "user":
            if image_base64:
                formatted_messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": msg["content"]},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                    ]
                })
            else:
                formatted_messages.append({
                    "role": "user",
                    "content": [{"type": "text", "text": msg["content"]}]
                })

    body = {
        "model": model,
        "messages": formatted_messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False  # Disable streaming, we want full JSON response
    }

    # Smart endpoint construction - avoid double /v1/
    if url.endswith('/v1') or url.endswith('/v1/'):
        # URL already has /v1, just add /chat/completions
        endpoint = f"{url.rstrip('/')}/chat/completions"
    elif is_local_url(url):
        # Local URL without /v1, add full path
        endpoint = f"{url}/v1/chat/completions"
    else:
        # Cloud API, just add /chat/completions
        endpoint = f"{url}/chat/completions"

    print(f"[UniversalLLM V2] Calling API: {endpoint}")
    print(f"[UniversalLLM V2] Model: {model}, Temperature: {temperature}, Max tokens: {max_tokens}")

    try:
        timeout = aiohttp.ClientTimeout(total=120)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(endpoint, headers=headers, json=body) as response:
                if response.status != 200:
                    error_msg = f"API Error {response.status}"
                    try:
                        error_json = await response.json()
                        error_msg += f": {error_json.get('error', {}).get('message', 'Unknown error')}"
                    except:
                        text = await response.text()
                        error_msg += f": {text[:200]}"
                    return None, error_msg

                # Check if response is streaming (text/event-stream)
                content_type = response.headers.get('Content-Type', '')

                if 'text/event-stream' in content_type or 'stream' in content_type:
                    # Handle streaming response
                    print("[UniversalLLM V2] Detected streaming response, collecting chunks...")
                    full_content = ""
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data: '):
                            data_str = line_text[6:]  # Remove 'data: ' prefix
                            if data_str == '[DONE]':
                                break
                            try:
                                import json
                                chunk = json.loads(data_str)
                                if "choices" in chunk and len(chunk["choices"]) > 0:
                                    delta = chunk["choices"][0].get("delta", {})
                                    content_chunk = delta.get("content", "")
                                    if content_chunk:
                                        full_content += content_chunk
                            except:
                                continue

                    if full_content:
                        print(f"[UniversalLLM V2] ✓ Success! Collected {len(full_content)} characters from stream")
                        return full_content, None
                    else:
                        return None, "Empty streaming response"

                else:
                    # Handle regular JSON response
                    response_json = await response.json()

                    if "choices" in response_json and len(response_json["choices"]) > 0:
                        content = response_json["choices"][0].get("message", {}).get("content", "")

                        usage = response_json.get("usage", {})
                        prompt_tokens = usage.get("prompt_tokens", 0)
                        completion_tokens = usage.get("completion_tokens", 0)
                        total_tokens = prompt_tokens + completion_tokens

                        print(f"[UniversalLLM V2] ✓ Success! Tokens: {prompt_tokens} + {completion_tokens} = {total_tokens}")

                        return content, None
                    else:
                        return None, "No response content from model"

    except asyncio.TimeoutError:
        return None, "Request timeout (120s)"
    except aiohttp.ClientError as e:
        return None, f"Network error: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"


# ══════════════════════════════════════════════════════════════════════════
# COMFYUI NODE (Modern V2)
# ══════════════════════════════════════════════════════════════════════════
class UniversalLLMPromptNodeV2(ComfyNodeABC):
    """Universal LLM Prompt Generator for ComfyUI (Async Version)"""

    DESCRIPTION = "Modern async LLM prompt generator with non-blocking API calls"
    CATEGORY = "LLM"

    @classmethod
    def INPUT_TYPES(cls) -> InputTypeDict:
        preset_keys = list(SYSTEM_PROMPTS.keys())
        default_preset = preset_keys[0] if preset_keys else "Empty (use your own)"

        return {
            "required": {
                "prompt": (IO.STRING, {
                    "multiline": True,
                    "default": "a woman in a red dress standing on a rain-soaked rooftop at night",
                }),
                "system_prompt_preset": (preset_keys, {
                    "default": default_preset,
                }),
                "system_prompt_custom": (IO.STRING, {
                    "multiline": True,
                    "default": "",
                }),
                "url": (IO.STRING, {
                    "default": "http://127.0.0.1:8080",
                }),
                "api_key": (IO.STRING, {
                    "default": "",
                }),
                "model": (IO.STRING, {
                    "default": "qwen2-vl:7b",
                }),
                "temperature": (IO.FLOAT, {
                    "default": 0.7,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.01,
                }),
                "max_tokens": (IO.INT, {
                    "default": 1000,
                    "min": 1,
                    "max": 32000,
                    "step": 1,
                }),
                "image_resize": (IO.BOOLEAN, {
                    "default": True,
                }),
                "resize_width": (IO.INT, {
                    "default": 1024,
                    "min": 256,
                    "max": 2048,
                    "step": 64,
                }),
                "resize_height": (IO.INT, {
                    "default": 1024,
                    "min": 256,
                    "max": 2048,
                    "step": 64,
                }),
            },
            "optional": {
                "image": (IO.IMAGE,),
            }
        }

    RETURN_TYPES = (IO.STRING,)
    RETURN_NAMES = ("generated_prompt",)
    FUNCTION = "execute"

    async def execute(
        self,
        prompt: str,
        system_prompt_preset: str,
        system_prompt_custom: str,
        url: str,
        api_key: str,
        model: str,
        temperature: float,
        max_tokens: int,
        image_resize: bool,
        resize_width: int,
        resize_height: int,
        image: Optional[torch.Tensor] = None
    ) -> Tuple[str]:
        """Execute LLM prompt generation (async)"""
        result = await self._execute_async(
            prompt, system_prompt_preset, system_prompt_custom,
            url, api_key, model, temperature, max_tokens,
            image_resize, resize_width, resize_height, image
        )
        return (result,)

    async def _execute_async(
        self,
        prompt: str,
        system_prompt_preset: str,
        system_prompt_custom: str,
        url: str,
        api_key: str,
        model: str,
        temperature: float,
        max_tokens: int,
        image_resize: bool,
        resize_width: int,
        resize_height: int,
        image: Optional[torch.Tensor] = None
    ) -> str:
        """Async execution logic"""

        # Validation
        if not prompt or not prompt.strip():
            return "Error: Prompt is required"

        if not url or not url.strip():
            return "Error: URL is required"

        if not model or not model.strip():
            return "Error: Model name is required"

        url = url.rstrip("/")

        # Determine system prompt
        if system_prompt_preset.startswith("Empty"):
            system_prompt = system_prompt_custom
        else:
            system_prompt = SYSTEM_PROMPTS.get(system_prompt_preset, "")

        # Build messages
        messages = []
        if system_prompt and system_prompt.strip():
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        # Process image if provided
        image_base64 = None
        if image is not None:
            try:
                print("[UniversalLLM V2] Processing image input...")
                pil_image = tensor_to_pil(image)

                if image_resize:
                    pil_image = resize_image_smart(pil_image, resize_width, resize_height)

                image_base64 = pil_to_base64(pil_image)
                print(f"[UniversalLLM V2] Image ready: {pil_image.size[0]}x{pil_image.size[1]}")
            except Exception as e:
                return f"Error processing image: {str(e)}"
        else:
            print("[UniversalLLM V2] Running in text-only mode")

        # API MODE - call external API
        mode = "llama.cpp" if is_local_url(url) else "API"
        print(f"[UniversalLLM V2] Mode: {mode}")

        result, error = await call_llm_api_async(
            url=url,
            api_key=api_key,
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            image_base64=image_base64
        )

        if error:
            return f"Error: {error}"

        if not result or not result.strip():
            return "Error: Empty response from model"

        print(f"[UniversalLLM V2] Generated prompt length: {len(result)} characters")
        return result


# ══════════════════════════════════════════════════════════════════════════
# COMFYUI REGISTRATION
# ══════════════════════════════════════════════════════════════════════════
NODE_CLASS_MAPPINGS = {
    "UniversalLLMPromptNodeV2": UniversalLLMPromptNodeV2
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "UniversalLLMPromptNodeV2": "Universal LLM Prompt V2 (Async)"
}

print("[UniversalLLM V2] Async node registered successfully!")
