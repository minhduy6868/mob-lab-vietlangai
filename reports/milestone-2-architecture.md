# Mốc 2 — Kiến trúc

## Ba phần

`fe` gọi `be`. `be` gọi `ai-model`. Cả hai process Python đọc `shared/languages.json`. Flutter giữ bản catalog local và đồng bộ.

```text
Flutter (SQLite + OCR trên máy)
    |  JWT, sync, dịch, quiz
Python API  -- PostgreSQL Supabase
    |  HTTP
Python ML   -- glossary, sau này mT5 / NLLB / Whisper
```

## Quyết định

- Một mô hình mT5 cho các cặp dân tộc ↔ Việt. NLLB chỉ cho Việt ↔ Anh.
- Tiếng Anh từ câu dân tộc đi qua tiếng Việt.
- Đóng góp có `client_id` để gửi lại không tạo bản trùng.
- Đáp án quiz không ra khỏi API và không nằm trong view `quiz_choices_public`.
- OCR Latin trên máy là tính năng AI tại thiết bị. ASR server để sau, H'Mông trước.

## Rủi ro

| Rủi ro | Cách xử lý |
| --- | --- |
| Chăm và Jrai ít câu song song | Chuyển giao từ Ê Đê, không bịa câu |
| Chính tả H'Mông khác RPA | Không dùng model Hmong–Thái |
| Mất mạng | SQLite giữ catalog và câu chờ |
| Pooler Supabase | Tắt prepared statement của asyncpg |
