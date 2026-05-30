# Flood Severity Dataset README

## 1. Mục đích dataset

Dataset này dùng để huấn luyện mô hình phân loại mức độ ngập lụt trong ảnh phục vụ đề tài NCKH về nhận diện mức độ ngập từ hình ảnh thực tế.

Bài toán hiện tại là **image classification** với 4 lớp:

| Label | Ý nghĩa |
|---|---|
| `non` | Không ngập |
| `low` | Ngập thấp |
| `medium` | Ngập vừa |
| `high` | Ngập cao |

---

## 2. Cấu trúc thư mục đề xuất

```text
Dataset/
├── train/
│   ├── non/
│   ├── low/
│   ├── medium/
│   └── high/
│
├── val/
│   ├── non/
│   ├── low/
│   ├── medium/
│   └── high/
│
├── test/
│   ├── non/
│   ├── low/
│   ├── medium/
│   └── high/
│
├── _review/
│   ├── ambiguous/
│   ├── duplicate/
│   └── same_filename_different_image/
│
├── image_manifest.csv
└── README.md
```

### Ý nghĩa các thư mục

| Thư mục | Mục đích |
|---|---|
| `train/` | Dữ liệu dùng để huấn luyện model |
| `val/` | Dữ liệu dùng để chọn checkpoint tốt nhất và điều chỉnh mô hình |
| `test/` | Dữ liệu chỉ dùng để đánh giá cuối cùng, không dùng để tuning |
| `_review/ambiguous/` | Ảnh khó phân loại, cần kiểm tra lại thủ công |
| `_review/duplicate/` | Ảnh trùng hoặc gần trùng |
| `_review/same_filename_different_image/` | Ảnh cùng tên file nhưng nội dung khác nhau |
| `image_manifest.csv` | File thống kê toàn bộ ảnh, nhãn, đường dẫn, hash, split |

---

## 3. Quy tắc phân loại nhãn

### 3.1. `non` — Không ngập

Ảnh thuộc lớp `non` khi:

- Không thấy nước ngập trên đường, sân, nhà hoặc khu vực sinh hoạt.
- Chỉ có mưa, đường ướt, mặt đường phản chiếu ánh nước nhưng **không có nước đọng/ngập rõ ràng**.
- Có nước tự nhiên như sông, ao, hồ, kênh rạch nhưng **không tràn vào khu vực đường/nhà/sinh hoạt**.
- Ảnh chỉ thể hiện thời tiết xấu, trời mưa, mây đen nhưng không có dấu hiệu ngập.

Ví dụ nên gán `non`:

```text
- Đường ướt sau mưa nhưng xe vẫn chạy bình thường.
- Có mưa nhưng không thấy nước ngập mặt đường.
- Ảnh sông/kênh bình thường, không tràn bờ.
```

---

### 3.2. `low` — Ngập thấp

Ảnh thuộc lớp `low` khi:

- Nước ngập thấp, thường **dưới đầu gối người**.
- Nước chỉ ngập một phần mặt đường, sân, hẻm.
- Với xe máy: nước chỉ tới phần thấp của bánh xe hoặc phần dưới thân xe.
- Với ô tô: nước **dưới bánh xe hoặc chỉ chạm rất thấp ở bánh xe**, chưa vượt quá bánh xe rõ ràng.
- Người vẫn có thể đi qua tương đối dễ, chưa có dấu hiệu nguy hiểm cao.

Mốc nhận biết chính:

```text
Người: dưới gối
Xe máy: dưới thân xe / dưới yên xe
Ô tô: dưới bánh xe hoặc rất thấp ở bánh xe
```

Ví dụ nên gán `low`:

```text
- Nước ngập mắt cá hoặc bắp chân.
- Xe máy chạy qua vùng nước nông.
- Đường có nước đọng nhưng chưa che bánh xe ô tô.
```

---

### 3.3. `medium` — Ngập vừa

Ảnh thuộc lớp `medium` khi:

- Nước ngập khoảng **từ đầu gối trở lên nhưng chưa tới ngực người**.
- Với người: nước ở mức đầu gối, đùi, hông, bụng hoặc dưới ngực.
- Với xe máy: nước tới **yên xe** hoặc cao hơn yên xe nhưng chưa vượt tay lái.
- Với ô tô: nước **vượt bánh xe**, ngập đến thân xe/cửa xe nhưng chưa tới cửa kính hoặc nóc xe.
- Mức ngập ảnh hưởng rõ đến di chuyển và sinh hoạt.

Mốc nhận biết chính:

```text
Người: từ gối đến dưới ngực
Xe máy: tới yên xe hoặc cao hơn yên
Ô tô: trên bánh xe, tới thân/cửa xe
```

Ví dụ nên gán `medium`:

```text
- Người lội nước ngang đùi hoặc ngang hông.
- Xe máy bị ngập tới yên.
- Ô tô bị ngập quá bánh xe nhưng chưa tới cửa kính.
```

---

### 3.4. `high` — Ngập cao

Ảnh thuộc lớp `high` khi:

- Nước ngập **từ ngực người trở lên**.
- Với xe máy: nước vượt tay lái hoặc gần như nhấn chìm xe.
- Với ô tô: nước chạm hoặc vượt **cửa kính, kính xe, nóc xe**.
- Nhà cửa, sân, hẻm hoặc phương tiện bị ngập nặng.
- Có dấu hiệu nguy hiểm cao, khó di chuyển hoặc cần cứu hộ.

Mốc nhận biết chính:

```text
Người: từ ngực trở lên
Xe máy: vượt tay lái
Ô tô: tới kính xe / nóc xe
```

Ví dụ nên gán `high`:

```text
- Người đứng trong nước ngang ngực.
- Ô tô bị ngập tới cửa kính hoặc gần nóc.
- Nhà bị nước ngập sâu vào bên trong, vật dụng nổi trên mặt nước.
```

---

## 4. Quy tắc xử lý ảnh ranh giới

Một số ảnh có thể nằm giữa hai mức. Khi phân loại, ưu tiên các mốc sau:

1. **Có người trong ảnh**: dùng cơ thể người làm mốc chính.
2. **Có xe máy**: dùng bánh xe, yên xe, tay lái làm mốc.
3. **Có ô tô**: dùng bánh xe, thân xe, cửa kính, nóc xe làm mốc.
4. **Không có vật chuẩn rõ ràng**: đánh dấu vào `_review/ambiguous/`.

### Quy tắc chọn nhãn khi phân vân

| Trường hợp | Nhãn nên chọn |
|---|---|
| Dưới gối nhưng nước phủ đường rõ | `low` |
| Gần gối hoặc vừa qua gối | `medium` |
| Từ hông đến dưới ngực | `medium` |
| Gần ngực nhưng chưa rõ tới ngực | `medium` hoặc đưa vào `_review/ambiguous/` |
| Tới ngực rõ ràng trở lên | `high` |
| Ô tô ngập tới cửa kính/nóc | `high` |
| Chỉ mưa, đường ướt, không ngập | `non` |

Nếu ảnh quá khó xác định, **không nên ép nhãn**, hãy đưa vào:

```text
_review/ambiguous/
```

---

## 5. Quy tắc làm sạch dữ liệu

### 5.1. Ảnh trùng hoàn toàn

Ảnh trùng hoàn toàn là ảnh có cùng nội dung và cùng hash.

Cách xử lý:

- Giữ lại 1 ảnh duy nhất.
- Xóa hoặc chuyển bản trùng vào `_review/duplicate/`.
- Không để cùng một ảnh xuất hiện ở nhiều split khác nhau như `train` và `val`.

---

### 5.2. Ảnh gần trùng

Ảnh gần trùng là ảnh có nội dung gần giống nhau nhưng có thể khác:

- Kích thước ảnh
- Độ sáng
- Crop nhẹ
- Nén lại
- Thêm watermark
- Đổi tên file

Cách xử lý:

- Nếu nội dung gần như giống hệt, chỉ giữ lại một ảnh.
- Nếu hai ảnh giống nhau nhưng bị gán hai nhãn khác nhau, cần kiểm tra lại nhãn thủ công.
- Không để ảnh gần trùng xuất hiện ở cả `train`, `val`, `test`.

---

### 5.3. Cùng tên file nhưng khác ảnh

Trường hợp này cần kiểm tra riêng vì có thể gây lỗi khi copy, merge dataset hoặc overwrite file.

Cách xử lý:

- Không xóa tự động.
- Chuyển vào `_review/same_filename_different_image/`.
- Đổi tên file theo format an toàn hơn.

Format tên file đề xuất:

```text
<label>_<source>_<index>.<ext>
```

Ví dụ:

```text
high_web_000001.jpg
medium_google_000123.jpg
low_facebook_000045.jpg
non_rain_000010.jpg
```

---

## 6. `image_manifest.csv`

File `image_manifest.csv` dùng để quản lý dataset và tránh lỗi trùng ảnh, sai nhãn, lệch split.

Các cột đề xuất:

| Cột | Ý nghĩa |
|---|---|
| `image_id` | ID duy nhất của ảnh |
| `file_name` | Tên file |
| `relative_path` | Đường dẫn tương đối trong dataset |
| `label` | Nhãn hiện tại |
| `split` | `train`, `val`, `test` hoặc `review` |
| `width` | Chiều rộng ảnh |
| `height` | Chiều cao ảnh |
| `file_size` | Dung lượng file |
| `md5` | Hash MD5 để phát hiện trùng tuyệt đối |
| `phash` | Perceptual hash để phát hiện ảnh gần trùng |
| `source` | Nguồn ảnh nếu có |
| `review_status` | `not_reviewed`, `reviewed`, `needs_fix` |
| `note` | Ghi chú thủ công |

---

## 7. Chia train / val / test

Tỷ lệ chia đề xuất:

```text
train: 70%
val:   15%
test:  15%
```

Hoặc:

```text
train: 80%
val:   10%
test:  10%
```

Yêu cầu quan trọng:

- Mỗi lớp phải có đủ ảnh trong cả `train`, `val`, `test`.
- Không để ảnh trùng hoặc gần trùng xuất hiện ở nhiều split.
- Split nên được chia theo ảnh gốc, không chia sau khi augmentation.
- `test` chỉ dùng để đánh giá cuối cùng, không dùng để chọn model.

---

## 8. Lưu ý khi train model

Dataset hiện có thể bị mất cân bằng giữa các lớp, đặc biệt lớp `high` thường ít ảnh hơn các lớp khác.

Khi train nên cân nhắc:

- Dùng `WeightedRandomSampler` hoặc class weight.
- Theo dõi `macro_f1`, `balanced_accuracy`, confusion matrix thay vì chỉ nhìn accuracy.
- Kiểm tra riêng các lỗi nhầm:
  - `low` → `medium`
  - `medium` → `high`
  - `non` ↔ `low`
- Dùng augmentation vừa phải, không làm biến dạng mốc ngập.
- Không dùng augmentation quá mạnh làm thay đổi ý nghĩa mực nước.

Metric nên theo dõi:

```text
accuracy
macro_f1
balanced_accuracy
per-class precision
per-class recall
confusion_matrix
```

---

## 9. Quy tắc augmentation

Nên dùng:

```text
- Resize
- Random crop nhẹ
- Horizontal flip
- Color jitter nhẹ
- Random rotation nhỏ
- Normalize theo ImageNet
```

Hạn chế hoặc tránh:

```text
- Crop quá mạnh làm mất người/xe/mốc nước
- Rotate quá lớn
- Blur quá mạnh
- CutMix/MixUp nếu làm mất ranh giới mực nước
- Augmentation làm nước trông sâu hoặc cạn khác thực tế
```

---

## 10. Quy trình cập nhật dataset

Khi thêm ảnh mới:

1. Đưa ảnh vào thư mục tạm.
2. Kiểm tra ảnh lỗi, ảnh quá mờ, ảnh không liên quan.
3. Gán nhãn theo guideline.
4. Kiểm tra duplicate và near-duplicate.
5. Cập nhật `image_manifest.csv`.
6. Chia vào `train`, `val`, `test`.
7. Train lại model hoặc đánh giá lại model.
8. Lưu kết quả experiment.

---

## 11. Quy tắc loại bỏ ảnh

Nên loại bỏ hoặc đưa vào `_review/ambiguous/` nếu:

- Ảnh quá mờ, quá tối, không nhìn rõ mực nước.
- Không xác định được khu vực có bị ngập hay không.
- Ảnh không liên quan đến ngập lụt.
- Ảnh minh họa, ảnh vẽ, ảnh AI-generated nếu dataset chỉ dùng ảnh thực tế.
- Ảnh có nhãn mâu thuẫn nhưng không đủ bằng chứng để sửa.

---

## 12. Checklist trước khi train

Trước khi train model, kiểm tra:

- [ ] Dataset có đủ 4 lớp: `non`, `low`, `medium`, `high`.
- [ ] Không có ảnh trùng giữa các lớp.
- [ ] Không có ảnh trùng giữa `train`, `val`, `test`.
- [ ] Các ảnh ranh giới đã được review.
- [ ] Không có ảnh lỗi hoặc file hỏng.
- [ ] Tên folder đúng với tên class trong code.
- [ ] `class_to_idx` đúng thứ tự mong muốn.
- [ ] `image_manifest.csv` đã được cập nhật.
- [ ] Kết quả thống kê số lượng ảnh mỗi lớp đã được ghi lại.
- [ ] `test` chưa từng được dùng để chọn checkpoint.

---

## 13. Thứ tự class khuyến nghị

Nên cố định thứ tự class trong code để tránh lệch mapping:

```python
CLASS_NAMES = ["non", "low", "medium", "high"]
```

Mapping tương ứng:

```python
class_to_idx = {
    "non": 0,
    "low": 1,
    "medium": 2,
    "high": 3
}
```

Khi load checkpoint để inference, phải dùng đúng mapping này.

---

## 14. Ghi chú về các trường hợp đã thống nhất

| Trường hợp ảnh | Nhãn đề xuất |
|---|---|
| Người đứng trong nước khoảng bụng, chưa tới ngực | `medium` |
| Người đi trong nước khoảng đùi/hông | `medium` |
| Ô tô ngập tới cửa kính hoặc gần nóc | `high` |
| Chỉ mưa, đường ướt, không thấy nước ngập | `non` |
| Nước phủ đường nông dưới gối | `low` |

---

## 15. Nguyên tắc quan trọng

Dataset tốt quan trọng hơn model phức tạp. Nếu nhãn chưa nhất quán, model sẽ học sai ranh giới giữa `low`, `medium`, `high`.

Ưu tiên hiện tại:

```text
1. Làm sạch nhãn
2. Loại duplicate / near-duplicate
3. Giữ mapping class cố định
4. Train baseline ResNet18 / MobileNetV3
5. Đánh giá bằng macro_f1, balanced_accuracy và confusion matrix
6. Review lại các ảnh model dự đoán sai
```
