# Mốc 1 — Phạm vi và tiêu chí

## Bài toán

Ngôn Sắc Việt dịch câu ngắn giữa tiếng dân tộc và tiếng Việt / tiếng Anh, nhận chữ từ ảnh, nhận giọng nói, nhận câu cộng đồng đã đối chiếu, lưu di sản và có bài học kèm quiz.

## Phạm vi học kỳ

Năm ngôn ngữ: Tày, Ê Đê, Chăm, H'Mông, Jrai. Đánh giá sâu hơn nếu dữ liệu lệch: Tày, Ê Đê, Chăm.

Không huấn luyện mô hình nền từ đầu. Không bịa câu tiếng dân tộc để demo.

## Tiêu chí xong việc

- Dịch được Việt ↔ Anh bằng cặp đã có, và dân tộc ↔ Việt khi đã có câu duyệt hoặc checkpoint.
- Ảnh trên Android/iOS đọc chữ tại máy rồi mới gửi đi dịch.
- Câu đóng góp lưu khi mất mạng, lên server thì vào hàng chờ, chỉ câu duyệt vào CSV huấn luyện.
- App có sáng/tối và hai ngôn ngữ giao diện.
- Postgres của bản nộp là Supabase.

## Phân công

| Người | Phần |
| --- | --- |
| Nguyễn Minh Duy 23IT038, Lương Thế Nguyên 23IT183 | `ai-model` |
| Bùi Thị Lệ Thắm 23IT253 | `be` |
| Trần Đình Nhứt 23IT203 | `fe` |
