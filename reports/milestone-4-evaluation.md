# Mốc 4 — Đánh giá và kịch bản demo

Điền số sau khi chạy. Không chép số từ bài báo khác vào cột của nhóm.

## Dịch chữ

| Cặp | Số câu test | chrF | BLEU | Ghi chú |
| --- | --- | --- | --- | --- |
| Tày → Việt |  |  |  |  |
| Ê Đê → Việt |  |  |  |  |
| Chăm → Việt |  |  |  |  |
| Việt → Anh |  |  |  | NLLB, không fine-tune |

Câu test không được nằm trong tập train. Câu chưa duyệt không được tính.

## OCR và mạng

| Tình huống | Kỳ vọng | Đạt |
| --- | --- | --- |
| Ảnh chữ Latin trên Android | ML Kit trả chữ, người dùng sửa, rồi dịch |  |
| Windows / web | Báo OCR trên máy không có, vẫn gõ được |  |
| Tắt mạng, gửi một câu đóng góp | Câu còn trong SQLite, trạng thái chờ |  |
| Bật mạng | Câu lên API đúng một lần theo `client_id` |  |
| Thành viên thường xuất CSV | 403 |  |
| Reviewer duyệt rồi xuất CSV | Chỉ câu `approved`, cột `verified=true` |  |

## Demo 8 phút

1. Đổi sáng/tối và Việt/Anh.
2. Mở Tày: địa bàn, họ ngôn ngữ, tư liệu chữ.
3. Dịch "Xin chào" từ Việt sang Anh.
4. Trên điện thoại, đọc một ảnh chữ Latin.
5. Tắt mạng, lưu một câu đóng góp, bật mạng, đăng nhập, đồng bộ.
6. Reviewer duyệt. Cho thấy câu đó chưa từng được mô hình bịa ra trước khi duyệt.
7. Làm một quiz. Chỉ ra đáp án không có trong JSON bài học.

## Giọng nói

Ghi WER khi có checkpoint H'Mông. Trước mốc đó, API trả `unloaded` và nói rõ model chưa nạp.
