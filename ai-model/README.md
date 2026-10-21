# AI model

Dịch câu ngắn cho Tày, Ê Đê, Chăm, H'Mông và Jrai. Mặc định dùng bảng câu đã duyệt. Cặp chưa có model trả `model_not_ready`, không bịa câu.

`mt5` dành cho tiếng dân tộc và tiếng Việt. `nllb` chỉ cho Việt và Anh. OCR và ASR trả `unloaded` cho đến khi có checkpoint đã kiểm tra.

Catalog nằm ở `shared/languages.json` (trong repo đủ, hoặc cạnh thư mục này). Có thể trỏ `LANGUAGES_CATALOG`.

```powershell
python -m pip install -e ".[dev]"
python -m uvicorn app.main:app --port 8100
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
python -m pytest
```

Nguồn dữ liệu nằm trong `RESEARCH.md`.
