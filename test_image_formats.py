"""
Test different image transmission formats to find what works with Omniroute
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


def pil_to_base64(pil_image: Image.Image, format: str = "PNG") -> str:
    """Convert PIL Image to base64 string"""
    buffered = python_io.BytesIO()
    pil_image.save(buffered, format=format)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


async def test_format(url: str, api_key: str, model: str, prompt: str, image_base64: str, format_name: str, body: dict) -> Tuple[str, Optional[str]]:
    """Test a specific format"""
    headers = {"Content-Type": "application/json"}

    if api_key and api_key.strip():
        headers["Authorization"] = f"Bearer {api_key}"

    endpoint = f"{url}/v1/chat/completions"

    print(f"\n[TEST] Testing format: {format_name}")
    print(f"[TEST] Body keys: {list(body.keys())}")

    try:
        timeout = aiohttp.ClientTimeout(total=60)
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
                    return format_name, error_msg

                response_json = await response.json()

                if "choices" in response_json and len(response_json["choices"]) > 0:
                    content = response_json["choices"][0].get("message", {}).get("content", "")
                    print(f"[TEST] ✓ Response: {content[:200]}...")

                    # Check if model actually saw the image
                    content_lower = content.lower()
                    if "unavailable" in content_lower or "don't see" in content_lower or "no image" in content_lower or "can't see" in content_lower:
                        return format_name, f"Model didn't see image: {content[:100]}"

                    return format_name, f"OK: {content[:100]}"
                else:
                    return format_name, "No response content"

    except Exception as e:
        return format_name, f"Error: {str(e)}"


class TestImageFormatsNode(ComfyNodeABC):
    """Test different image transmission formats"""

    DESCRIPTION = "Test different ways to send images to LLM API"
    CATEGORY = "LLM"

    @classmethod
    def INPUT_TYPES(cls) -> InputTypeDict:
        return {
            "required": {
                "prompt": (IO.STRING, {
                    "multiline": True,
                    "default": "Describe this image in detail",
                }),
                "url": (IO.STRING, {
                    "default": "http://localhost:20128",
                }),
                "api_key": (IO.STRING, {
                    "default": "sk-fff619f7ed927d1e-c58a39-0f971d8f",
                }),
                "model": ([
                    "nvidia/moonshotai/kimi-k2.6",
                    "nvidia/microsoft/phi-4-multimodal-instruct",
                    "nvidia/meta/llama-3.2-90b-vision-instruct",
                    "openrouter/qwen/qwen-2-vl-72b-instruct",
                    "openrouter/anthropic/claude-3.5-sonnet",
                ], {
                    "default": "nvidia/moonshotai/kimi-k2.6",
                }),
                "image_size": (IO.INT, {
                    "default": 512,
                    "min": 128,
                    "max": 2048,
                    "step": 64,
                }),
            },
            "optional": {
                "image": (IO.IMAGE,),
            }
        }

    RETURN_TYPES = (IO.STRING,)
    RETURN_NAMES = ("results",)
    FUNCTION = "execute"

    async def execute(
        self,
        prompt: str,
        url: str,
        api_key: str,
        model: str,
        image_size: int,
        image: Optional[torch.Tensor] = None
    ) -> Tuple[str]:
        """Test all formats"""

        if image is None:
            return ("Error: Image is required",)

        # Process image
        pil_image = tensor_to_pil(image)
        pil_image = pil_image.resize((image_size, image_size), Image.Resampling.LANCZOS)
        image_base64 = pil_to_base64(pil_image, "PNG")

        print(f"\n[TEST] Image size: {image_size}x{image_size}, base64 length: {len(image_base64)}")

        url = url.rstrip("/")

        # Format 1: Multimodal with system message
        body1 = {
            "model": model,
            "messages": [
                {"role": "system", "content": [{"type": "text", "text": "You are a helpful assistant."}]},
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                ]}
            ],
            "temperature": 0.3,
            "max_tokens": 100,
            "stream": False
        }

        # Format 2: Multimodal without system message
        body2 = {
            "model": model,
            "messages": [
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                ]}
            ],
            "temperature": 0.3,
            "max_tokens": 100,
            "stream": False
        }

        # Format 3: Simple string messages + image field
        body3 = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "image": f"data:image/png;base64,{image_base64}",
            "temperature": 0.3,
            "max_tokens": 100,
            "stream": False
        }

        # Format 4: Simple string messages + images array
        body4 = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "images": [f"data:image/png;base64,{image_base64}"],
            "temperature": 0.3,
            "max_tokens": 100,
            "stream": False
        }

        # Format 5: Multimodal with detail=low
        body5 = {
            "model": model,
            "messages": [
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/png;base64,{image_base64}",
                        "detail": "low"
                    }}
                ]}
            ],
            "temperature": 0.3,
            "max_tokens": 100,
            "stream": False
        }

        # Format 6: Multimodal with detail=high
        body6 = {
            "model": model,
            "messages": [
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/png;base64,{image_base64}",
                        "detail": "high"
                    }}
                ]}
            ],
            "temperature": 0.3,
            "max_tokens": 100,
            "stream": False
        }

        # Test all formats
        results = []

        formats = [
            ("Format 1: Multimodal + system", body1),
            ("Format 2: Multimodal no system", body2),
            ("Format 3: String + image field", body3),
            ("Format 4: String + images array", body4),
            ("Format 5: Multimodal detail=low", body5),
            ("Format 6: Multimodal detail=high", body6),
        ]

        for format_name, body in formats:
            result_name, error = await test_format(url, api_key, model, prompt, image_base64, format_name, body)
            if error:
                results.append(f"❌ {result_name}: {error}")
            else:
                results.append(f"✅ {result_name}: {error}")

        return ("\n".join(results),)


NODE_CLASS_MAPPINGS = {
    "TestImageFormatsNode": TestImageFormatsNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TestImageFormatsNode": "Test Image Formats"
}

print("[TestImageFormats] Node registered successfully!")
