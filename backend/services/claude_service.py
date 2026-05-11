import base64
import io
import json
import re

import anthropic
from PIL import Image

PARSE_PROMPT = """Analyze this receipt/bill image and extract all billing information.

Return a JSON object with EXACTLY this structure (no markdown, no explanation, raw JSON only):
{
  "items": [
    {"name": "item description", "quantity": 1, "unit_price": 0.00}
  ],
  "extras": {
    "vat": {"type": "percent", "value": 10.0},
    "service_charge": {"type": "fixed", "value": 5.00},
    "discount": null
  }
}

Rules:
- "type" must be "percent" if the receipt shows a percentage (e.g. "VAT 10%"), or "fixed" if it shows a currency amount
- Set extras fields to null if not present on the receipt
- "quantity" must be an integer >= 1
- All numeric values must be numbers, not strings, no currency symbols
- If an item has a quantity (e.g. "2x Burger"), set quantity accordingly
- Return your best estimate even if the image is partially unclear"""

MAX_BYTES = 4 * 1024 * 1024  # 4MB — safely under Claude's 5MB limit


def _compress_image(image_bytes: bytes) -> tuple[bytes, str]:
    """Resize and compress the image until it fits under MAX_BYTES."""
    img = Image.open(io.BytesIO(image_bytes))

    # Convert to RGB so we can always save as JPEG
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # Scale down if very large (max 2000px on longest side)
    max_dim = 2000
    if max(img.width, img.height) > max_dim:
        img.thumbnail((max_dim, max_dim), Image.LANCZOS)

    # Try decreasing quality until under the size limit
    for quality in (85, 70, 55, 40):
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality, optimize=True)
        data = buf.getvalue()
        if len(data) <= MAX_BYTES:
            return data, "image/jpeg"

    # Last resort: halve the resolution
    img = img.resize((img.width // 2, img.height // 2), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=40, optimize=True)
    return buf.getvalue(), "image/jpeg"


def parse_bill_image(image_bytes: bytes, ext: str, api_key: str) -> dict:
    # Compress before sending to Claude
    compressed, media_type = _compress_image(image_bytes)

    client = anthropic.Anthropic(api_key=api_key)
    b64 = base64.standard_b64encode(compressed).decode("utf-8")

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system="You are a bill/receipt parser. Always respond with valid JSON only — no markdown, no code fences, no explanation.",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": media_type, "data": b64},
                    },
                    {"type": "text", "text": PARSE_PROMPT},
                ],
            }
        ],
    )

    raw = message.content[0].text.strip()
    raw = re.sub(r"^```[a-z]*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)

    parsed = json.loads(raw)
    return {
        "items": _explode_items(parsed.get("items", [])),
        "extras": _normalize_extras(parsed.get("extras", {})),
    }


def _explode_items(claude_items: list) -> list:
    result = []
    for item in claude_items:
        qty = max(1, int(item.get("quantity", 1)))
        unit_price = float(item.get("unit_price", 0.0))
        for _ in range(qty):
            result.append({"description": item.get("name", "Item"), "amount": unit_price})
    return result


def _normalize_extras(extras: dict) -> dict:
    def clean(field):
        val = extras.get(field)
        if not val:
            return None
        return {"type": val.get("type", "fixed"), "value": float(val.get("value", 0))}

    return {
        "vat": clean("vat"),
        "service_charge": clean("service_charge"),
        "discount": clean("discount"),
    }
