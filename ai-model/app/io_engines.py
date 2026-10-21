def transcribe(audio: bytes, filename: str) -> dict:
    if not audio:
        return {
            "text": "",
            "engine": "unloaded",
            "warnings": ["Tệp âm thanh trống."],
        }
    return {
        "text": "",
        "engine": "unloaded",
        "warnings": [
            "Mô hình giọng nói chưa được nạp. Fine-tune Whisper và đặt ML_ASR_ENGINE=whisper khi checkpoint đã kiểm tra.",
            f"Đã nhận {len(audio)} byte từ {filename}.",
        ],
    }


def read_text(image: bytes, filename: str) -> dict:
    if not image:
        return {
            "text": "",
            "engine": "unloaded",
            "warnings": ["Tệp ảnh trống."],
        }
    return {
        "text": "",
        "engine": "unloaded",
        "warnings": [
            "OCR chưa được nạp. Ảnh Latin dùng PaddleOCR; chữ Chăm Akhar Thrah là mô hình riêng.",
            f"Đã nhận {len(image)} byte từ {filename}.",
        ],
    }
