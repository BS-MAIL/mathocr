import base64
import os
from pathlib import Path
from typing import Annotated

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ValidationError

APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parent
STATIC_DIR = APP_DIR / "static"

_ = load_dotenv(PROJECT_DIR / ".env")

API_BASE_URL = os.getenv("MATHBONG_BASE_URL", "https://llm.mathbong.com/v1").rstrip("/")
API_KEY = os.getenv("MATHBONG_API_KEY")
MODEL = os.getenv("MATHBONG_MODEL", "codex/gpt-5.5")

app = FastAPI(title="Math OCR", description="Convert math images to LaTeX.")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class ChatMessage(BaseModel):
    content: str


class ChatChoice(BaseModel):
    message: ChatMessage


class ChatCompletionResponse(BaseModel):
    choices: list[ChatChoice]


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/api/convert")
async def convert_to_latex(
    image: Annotated[UploadFile | None, File()] = None,
    image_data: Annotated[str | None, Form()] = None,
) -> dict[str, str]:
    if not API_KEY:
        raise HTTPException(status_code=500, detail="MATHBONG_API_KEY is not configured.")

    data_url = await build_image_data_url(image=image, image_data=image_data)
    payload = {
        "model": MODEL,
        "temperature": 0,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You convert images of math expressions into LaTeX. "
                    "Return only the LaTeX expression, with no Markdown fences or explanation."
                ),
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Convert the math expression in this image to LaTeX.",
                    },
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            },
        ],
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{API_BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {API_KEY}"},
                json=payload,
            )
            _ = response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text or exc.response.reason_phrase
        raise HTTPException(status_code=exc.response.status_code, detail=detail) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"API request failed: {exc}") from exc

    content = extract_message_content(response.content)
    return {"latex": content.strip()}


async def build_image_data_url(image: UploadFile | None, image_data: str | None) -> str:
    if image_data:
        if not image_data.startswith("data:image/") or ";base64," not in image_data:
            raise HTTPException(status_code=400, detail="Invalid canvas image data.")
        return image_data

    if image is None:
        raise HTTPException(status_code=400, detail="Upload an image or draw one first.")

    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded image is empty.")

    content_type = image.content_type or "image/png"
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image.")

    encoded = base64.b64encode(image_bytes).decode("ascii")
    return f"data:{content_type};base64,{encoded}"


def extract_message_content(data: bytes) -> str:
    try:
        parsed = ChatCompletionResponse.model_validate_json(data)
    except ValidationError as exc:
        raise HTTPException(status_code=502, detail="Unexpected API response format.") from exc

    if not parsed.choices:
        raise HTTPException(status_code=502, detail="API returned no choices.")

    content = parsed.choices[0].message.content
    if not content.strip():
        raise HTTPException(status_code=502, detail="API returned an empty result.")

    return content
