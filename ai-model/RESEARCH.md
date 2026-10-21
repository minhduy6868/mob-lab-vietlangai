# Nghiên cứu năm ngôn ngữ

Phạm vi đã chốt trong đề cương: Tày, Ê Đê, Chăm, H'Mông, Jrai. Ba ngôn ngữ đánh giá sâu trước là Tày, Ê Đê, Chăm. H'Mông và Jrai có trong sản phẩm, dữ liệu mỏng hơn thì mở rộng sau.

Dịch tiếng Anh không huấn luyện riêng. Câu dân tộc đi tới tiếng Việt, rồi Việt ↔ Anh bằng NLLB vì cặp này đã có sẵn.

## Tày (`tyz`)

- Họ Tai-Kadai, chữ Latin theo Quốc ngữ.
- Corpus công khai: [HeyDunaX/tay-vietnamese-nmt](https://huggingface.co/datasets/HeyDunaX/tay-vietnamese-nmt), 20.600 cặp, 2025.
- Nguyễn Long và cộng sự, workshop AAAI 2026, corpus Tày–Việt và Ba Na kèm mô hình: https://osf.io/fmq5k/ và bài [Not All Data Augmentation Works](https://longstnguyen.com/files/papers/nguyen-et-al-aaai-workshop-2026-not-all-data-augmentation-works.pdf).

## Ê Đê (`rad`)

- Nhóm Chamic, chữ Latin, Tây Nguyên.
- [NIRVLab/rhade-vietnamese-mt](https://huggingface.co/datasets/NIRVLab/rhade-vietnamese-mt), 17.097 cặp. Nguồn có văn bản tôn giáo; phải xem license trước khi huấn luyện.

## Chăm Đông (`cjm`)

- Cùng nhóm Chamic với Ê Đê và Jrai. Chữ truyền thống là Akhar Thrah; học liệu còn bản Latin.
- Có nghiên cứu dịch Việt–Chăm theo mẫu: https://champa.one/article/74. Câu song song neural công khai còn ít.
- Giai đoạn một: chuyển giao từ Ê Đê/Jrai cho bản Latin. OCR Akhar Thrah là việc riêng, không gộp vào OCR Latin.

## H'Mông (`hmn`)

- Họ Hmong-Mien. Chính tả Latin dùng ở Việt Nam khác RPA của cộng đồng hải ngoại.
- Âm thanh + chữ + tiếng Việt từ VOV: [elego/hmongv_audio_speaker03_3k_rows_30042026](https://huggingface.co/datasets/elego/hmongv_audio_speaker03_3k_rows_30042026). Đây là nguồn ASR đầu tiên.
- [Pakorn2112/whisper-model-large-hmong](https://huggingface.co/Pakorn2112/whisper-model-large-hmong) là Hmong–Thái / RPA. Chỉ tham khảo kỹ thuật, không dùng làm mô hình tiếng H'Mông Việt Nam.

## Jrai (`jra`)

- Chamic, gần Ê Đê, chữ Latin, Gia Lai và Kon Tum.
- Đỗ Thị Thuận, Đại học Đà Nẵng, 2012: dịch thống kê Jrai–Việt bằng Moses. Corpus không có trên Hugging Face.
- Từ điển đối chiếu khoảng 613 mục: https://glottosphere.com/dictionary/jra.
- Giai đoạn một dùng chuyển giao từ Ê Đê, giữ chính tả Jrai khi nhập câu mới.

## Mô hình

1. Một checkpoint `google/mt5-small`, tiền tố `{nguồn} {đích}: {câu}`, chỉ học CSV đã duyệt. Script: `training/finetune_mt5.py`.
2. Việt ↔ Anh: `facebook/nllb-200-distilled-600M`, không fine-tune trong đồ án.
3. Nhận dạng ngôn ngữ Latin dân tộc để sau (fastText hoặc bộ phân loại nhỏ). Heuristic hiện tại chỉ chắc chữ Chăm, tiếng Việt và tiếng Anh.
4. Giọng nói sau bản dịch chữ: Whisper nhỏ, H'Mông trước vì đã có audio.
5. Ảnh chữ Latin trên điện thoại dùng ML Kit. Ảnh gửi server vẫn là đường dự phòng khi máy không có OCR.

## Không đưa vào năm ngôn ngữ này

Khmer có corpus VOV lớn và NLLB (`khm_Khmr`), bài SOICT 2024 của HUST. Ba Na có corpus EAAI 2024 khoảng 20.000 cặp. Cơ Ho có ViKhoMT. Mường có `mr4/trans-vi-mu` nhưng dữ liệu không công khai. Giữ làm phương án mở rộng, không thay năm ngôn ngữ đã chốt.
