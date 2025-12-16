from typing import Any
import os
from openai import AsyncOpenAI

TOKEN = os.getenv("TOKEN", "cashuBpGFkYGF0g...")
BASE_URL = os.getenv("BASE_URL", "https://api.routstr.com/v1")
MODEL = os.getenv("MODEL", "deepcogito/cogito-v2-preview-llama-109b-moe")
PROMPT = os.getenv(
    "PROMPT",
    (
        "You are Golden Goose an advanced developer bot active on nostr! Keep responses under 512 chars. "
    ),
)

client = AsyncOpenAI(api_key=TOKEN, base_url=BASE_URL)


async def generate_ai_response(messages: list[dict[str, str]], **kwargs: Any) -> str:
    print(f"Generating AI response for messages: {len(messages)}")
    resp = await client.chat.completions.create(
        model=MODEL,
        messages=messages,
        **kwargs,
    )
    response_content = (resp.choices[0].message.content or "").strip()
    print(
        f"AI response: {response_content[:50]}{'...' if len(response_content) > 50 else ''}"
    )
    return response_content
