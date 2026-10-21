# Ngôn Sắc Việt

Nền tảng dịch, học và lưu di sản tiếng dân tộc. Giai đoạn này làm Tày, Ê Đê, Chăm, H'Mông và Jrai. Trọng tâm là dịch câu ngắn sang tiếng Việt và tiếng Anh, từ chữ, ảnh và giọng nói, cộng với câu do cộng đồng đóng góp sau khi được duyệt.

| Thư mục | Việc | Phụ trách |
| --- | --- | --- |
| `ai-model` | Mô hình dịch, sau đó giọng nói | Nguyễn Minh Duy 23IT038, Lương Thế Nguyên 23IT183 |
| `be` | API, luồng người dùng, PostgreSQL Supabase | Bùi Thị Lệ Thắm 23IT253, nhóm trưởng |
| `fe` | Ứng dụng Flutter | Trần Đình Nhứt 23IT203 |

Cả nhóm hỗ trợ test và nối phần của nhau. Hợp đồng chung là JSON của API và file `shared/languages.json`.

## Chạy local

Chưa có project Supabase thì API dùng SQLite. Khi có project, dán connection string vào `be/.env` theo `be/.env.example`, rồi chạy `be/supabase/migrations/0001_init.sql` trong SQL editor.

```powershell
cd ai-model
python -m pip install -e ".[dev]"
python -m uvicorn app.main:app --port 8100

cd ..\be
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
.\.venv\Scripts\python -m uvicorn app.main:app --port 8000

cd ..\fe
flutter pub get
dart run build_runner build
flutter run
```

Tài khoản rà soát local: `demo@ngonsacviet.example.com` / `Demo1234`.

Điện thoại Android emulator gọi API bằng `--dart-define=API_BASE=http://10.0.2.2:8000`. Supabase anon key, nếu dùng đọc catalog trực tiếp:

```powershell
flutter run --dart-define=SUPABASE_URL=https://PROJECT.supabase.co --dart-define=SUPABASE_ANON_KEY=...
```

Câu đóng góp vẫn gửi qua API để một chỗ duyệt. OCR chữ trên máy chỉ có ở bản Android và iOS.

## Kiểm tra

```powershell
cd ai-model; $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'; python -m pytest
cd ..\be; $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'; .\.venv\Scripts\python -m pytest
cd ..\fe; flutter test
```

Biến `PYTEST_DISABLE_PLUGIN_AUTOLOAD` chỉ cần khi máy đã cài plugin pytest khác làm hỏng lúc thu thập test.
