from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.catalog import load_catalog
from app.detect import detect_language
from app.io_engines import read_text, transcribe
from app.translate import RouteNotReady, Translator, UnknownLanguage, build_translator

app = FastAPI(title="Ngon Sac Viet ML", version="0.1.0")
_translator: Translator | None = None


def translator() -> Translator:
    global _translator
    if _translator is None:
        _translator = build_translator()
    return _translator


class TranslateIn(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    source_lang: str = "auto"
    target_lang: str


class DetectIn(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "ml"}


@app.get("/v1/languages")
def languages() -> list[dict]:
    return load_catalog()["languages"]


@app.post("/v1/detect")
def detect(body: DetectIn) -> dict:
    return detect_language(body.text)


@app.post("/v1/translate")
def translate(body: TranslateIn) -> dict:
    try:
        return translator().translate(body.text, body.source_lang, body.target_lang)
    except UnknownLanguage as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "unknown_language", "message": f"Không có mã ngôn ngữ {exc.code}."},
        ) from exc
    except RouteNotReady as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "model_not_ready",
                "message": "Chưa có mô hình hoặc cặp câu đã rà soát cho hướng dịch này.",
                "source_lang": exc.source,
                "target_lang": exc.target,
            },
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "empty_text", "message": "Văn bản trống."},
        ) from exc


@app.post("/v1/ocr")
async def ocr(file: UploadFile = File(...)) -> dict:
    data = await file.read()
    return read_text(data, file.filename or "image")


@app.post("/v1/asr")
async def asr(file: UploadFile = File(...)) -> dict:
    data = await file.read()
    return transcribe(data, file.filename or "audio")
