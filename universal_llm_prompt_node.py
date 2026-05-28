"""
Universal LLM Prompt Generator Node for ComfyUI (Simple Version)
=================================================================
Supports both cloud APIs and local llama.cpp servers.
Works with text-only and vision models.
"""

import json
import requests
import base64
import io as python_io
from PIL import Image
import torch
from torchvision.transforms import ToPILImage
import os


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
            print(f"[UniversalLLM] Loaded {len(presets)} presets from {presets_path}")
            return presets
    except Exception as e:
        print(f"[UniversalLLM] Error loading presets: {e}")
        return {"Empty (use your own)": ""}

SYSTEM_PROMPTS = load_presets()


# ══════════════════════════════════════════════════════════════════════════
# IMAGE PROCESSING
# ══════════════════════════════════════════════════════════════════════════
def resize_image_smart(pil_image, target_width=1024, target_height=1024):
    """Resize image to exact target dimensions"""
    width, height = pil_image.size

    if width == target_width and height == target_height:
        print(f"[UniversalLLM] Image already at target size: {width}x{height}")
        return pil_image

    print(f"[UniversalLLM] Resizing image: {width}x{height} → {target_width}x{target_height}")
    return pil_image.resize((target_width, target_height), Image.Resampling.LANCZOS)


def tensor_to_pil(image_tensor):
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


def pil_to_base64(pil_image):
    """Convert PIL Image to base64 string"""
    buffered = python_io.BytesIO()
    pil_image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


# ══════════════════════════════════════════════════════════════════════════
# API COMMUNICATION
# ══════════════════════════════════════════════════════════════════════════
def is_local_url(url):
    """Check if URL is localhost"""
    return "localhost" in url.lower() or "127.0.0.1" in url


def call_llm_api(url, api_key, model, messages, temperature, max_tokens, image_base64=None):
    """Universal LLM API caller"""
    headers = {"Content-Type": "application/json"}

    if api_key and api_key.strip():
        headers["Authorization"] = f"Bearer {api_key}"

    formatted_messages = []
    for msg in messages:
        if msg["role"] == "system":
            formatted_messages.append(msg)
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
                formatted_messages.append(msg)

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

    print(f"[UniversalLLM] Calling API: {endpoint}")
    print(f"[UniversalLLM] Model: {model}, Temperature: {temperature}, Max tokens: {max_tokens}")

    try:
        response = requests.post(endpoint, headers=headers, json=body, timeout=120, stream=True)

        # Force UTF-8 encoding for response
        response.encoding = 'utf-8'

        if response.status_code != 200:
            error_msg = f"API Error {response.status_code}"
            try:
                error_json = response.json()
                error_msg += f": {error_json.get('error', {}).get('message', 'Unknown error')}"
            except:
                error_msg += f": {response.text[:200]}"
            return None, error_msg

        # Check if response is streaming
        content_type = response.headers.get('Content-Type', '')

        if 'text/event-stream' in content_type or 'stream' in content_type:
            # Handle streaming response
            print("[UniversalLLM] Detected streaming response, collecting chunks...")
            full_content = ""
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data: '):
                        data_str = line_text[6:]  # Remove 'data: ' prefix
                        if data_str == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data_str)
                            if "choices" in chunk and len(chunk["choices"]) > 0:
                                delta = chunk["choices"][0].get("delta", {})
                                content_chunk = delta.get("content", "")
                                if content_chunk:
                                    full_content += content_chunk
                        except:
                            continue

            if full_content:
                print(f"[UniversalLLM] ✓ Success! Collected {len(full_content)} characters from stream")
                return full_content, None
            else:
                return None, "Empty streaming response"

        else:
            # Handle regular JSON response
            response_json = response.json()

            if "choices" in response_json and len(response_json["choices"]) > 0:
                content = response_json["choices"][0].get("message", {}).get("content", "")

                usage = response_json.get("usage", {})
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)
                total_tokens = prompt_tokens + completion_tokens

                print(f"[UniversalLLM] ✓ Success! Tokens: {prompt_tokens} + {completion_tokens} = {total_tokens}")

                return content, None
            else:
                return None, "No response content from model"

    except requests.exceptions.Timeout:
        return None, "Request timeout (120s)"
    except requests.exceptions.RequestException as e:
        return None, f"Network error: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"


# ══════════════════════════════════════════════════════════════════════════
# COMFYUI NODE
# ══════════════════════════════════════════════════════════════════════════
class UniversalLLMPromptNode:
    """Universal LLM Prompt Generator for ComfyUI"""

    @classmethod
    def INPUT_TYPES(cls):
        preset_keys = list(SYSTEM_PROMPTS.keys())
        default_preset = preset_keys[0] if preset_keys else "Empty (use your own)"

        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "a woman in a red dress standing on a rain-soaked rooftop at night",
                }),
                "system_prompt_preset": (preset_keys, {
                    "default": default_preset,
                }),
                "system_prompt_custom": ("STRING", {
                    "multiline": True,
                    "default": "",
                }),
                "url": ("STRING", {
                    "default": "http://127.0.0.1:8080",
                }),
                "api_key": ("STRING", {
                    "default": "",
                }),
                "model": ("STRING", {
                    "default": "qwen2-vl:7b",
                }),
                "temperature": ("FLOAT", {
                    "default": 0.7,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.01,
                }),
                "max_tokens": ("INT", {
                    "default": 1000,
                    "min": 1,
                    "max": 32000,
                    "step": 1,
                }),
                "image_resize": ("BOOLEAN", {
                    "default": True,
                }),
                "resize_width": ("INT", {
                    "default": 1024,
                    "min": 256,
                    "max": 2048,
                    "step": 64,
                }),
                "resize_height": ("INT", {
                    "default": 1024,
                    "min": 256,
                    "max": 2048,
                    "step": 64,
                }),
            },
            "optional": {
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("generated_prompt",)
    FUNCTION = "execute"
    CATEGORY = "LLM"
    OUTPUT_NODE = True

    def execute(self, prompt, system_prompt_preset, system_prompt_custom, url, api_key,
                model, temperature, max_tokens, image_resize, resize_width, resize_height, image=None):
        """Execute LLM prompt generation"""

        if not prompt or not prompt.strip():
            return ("Error: Prompt is required",)

        if not url or not url.strip():
            return ("Error: URL is required",)

        if not model or not model.strip():
            return ("Error: Model name is required",)

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
                print("[UniversalLLM] Processing image input...")
                pil_image = tensor_to_pil(image)

                if image_resize:
                    pil_image = resize_image_smart(pil_image, resize_width, resize_height)

                image_base64 = pil_to_base64(pil_image)
                print(f"[UniversalLLM] Image ready: {pil_image.size[0]}x{pil_image.size[1]}")
            except Exception as e:
                return (f"Error processing image: {str(e)}",)
        else:
            print("[UniversalLLM] Running in text-only mode")

        # Call API
        mode = "llama.cpp" if is_local_url(url) else "API"
        print(f"[UniversalLLM] Mode: {mode}")

        result, error = call_llm_api(
            url=url,
            api_key=api_key,
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            image_base64=image_base64
        )

        if error:
            return (f"Error: {error}",)

        if not result or not result.strip():
            return ("Error: Empty response from model",)

        print(f"[UniversalLLM] Generated prompt length: {len(result)} characters")
        return (result,)


# ══════════════════════════════════════════════════════════════════════════
# COMFYUI REGISTRATION
# ══════════════════════════════════════════════════════════════════════════
NODE_CLASS_MAPPINGS = {
    "UniversalLLMPromptNode": UniversalLLMPromptNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "UniversalLLMPromptNode": "Universal LLM Prompt"
}

print("[UniversalLLM] Node registered successfully!")
