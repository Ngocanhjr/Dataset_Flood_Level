# README - Lọc ảnh duplicate cho folder `high1`

Tài liệu này hướng dẫn cách dùng script `find_duplicate.py` để lọc ảnh trùng trong folder `high1`.

Bản script này được cập nhật để tránh lỗi cài đặt `pandas`, `numpy`, `imagehash`, `cmake`, `ninja` trên Windows/MSYS2.

---

## 1. Cấu trúc thư mục hiện tại

Ví dụ cấu trúc folder `DATA`:

```text
DATA/
├── Dataset_relabel/
│   ├── high/
│   ├── low/
│   ├── medium/
│   └── non_flood/
├── high1/
├── find_duplicate_images_no_pandas.py
└── duplicate_report_high1/
```

Trong đó:

| Thành phần                | Ý nghĩa                                               |
| ------------------------- | ----------------------------------------------------- |
| `high1/`                  | Folder ảnh mới cần lọc, chỉ chứa ảnh, chưa chia label |
| `Dataset_relabel/`        | Dataset đã chia label                                 |
| `find_duplicate.py`       | Script lọc duplicate                                  |
| `duplicate_report_high1/` | Folder xuất report sau khi chạy script                |

---

## 2. Script này dùng để làm gì?

Script hỗ trợ 3 việc chính:

1. Tìm ảnh trùng bên trong folder `high1`.
2. So sánh ảnh trong `high1` với `Dataset_relabel/high`.
3. Phát hiện ảnh trong `high1` bị trùng với label khác như:
   - `low`
   - `medium`
   - `non_flood`

Mặc định script chỉ xuất file `.csv`, chưa xoá ảnh và chưa move ảnh.

---

## 3. Ưu điểm của bản `no_pandas`

Bản này không dùng:

```text
pandas
numpy
imagehash
cmake
ninja
```

Vì vậy tránh lỗi kiểu:

```text
ERROR: Failed building wheel for cmake
ERROR: Failed to build numpy
ERROR: Failed to build pandas
SSL: CERTIFICATE_VERIFY_FAILED
```

Script có thể chạy ở chế độ `exact` mà không cần cài thêm thư viện nào.

---

## 4. Các chế độ chạy

Script có 3 mode:

| Mode    | Ý nghĩa                                 | Cần cài thư viện thêm không? |
| ------- | --------------------------------------- | ---------------------------- |
| `exact` | So sánh ảnh trùng hoàn toàn bằng SHA256 | Không cần                    |
| `ahash` | So sánh ảnh gần giống bằng average hash | Cần Pillow                   |
| `both`  | Chạy cả `exact` và `ahash`              | Cần Pillow                   |

Khuyến nghị chạy trước bằng:

```bash
--mode exact
```

Sau đó nếu cần bắt ảnh gần giống như resize/nén lại thì chạy thêm:

```bash
--mode both
```

---

## 5. Cài thư viện

### 5.1. Nếu chỉ chạy exact duplicate

Không cần cài gì thêm.

Chạy trực tiếp:

```bash
python find_duplicate.py --source high1 --source-label high --out duplicate_report_high1 --mode exact
```

---

### 5.2. Nếu muốn bắt ảnh gần giống

Cài thêm Pillow:

```bash
python -m pip install --upgrade pip
python -m pip install --upgrade Pillow
```

Nếu máy có nhiều Python, thử:

```bash
py -m pip install --upgrade pip
py -m pip install --upgrade Pillow
```

Sau đó có thể chạy:

```bash
python find_duplicate.py --source high1 --source-label high --compare-root Dataset_relabel --out duplicate_report_high1 --mode both --ahash-threshold 3
```

---

## 6. Lệnh 1 - Chỉ lọc duplicate bên trong `high1`

Lệnh này chỉ tạo report, chưa move ảnh:

```bash
python find_duplicate.py --source high1 --source-label high --out duplicate_report_high1 --mode exact
```

Sau khi chạy xong, kiểm tra file:

```text
duplicate_report_high1/duplicates_inside_high1.csv
```

File này cho biết ảnh nào trong `high1` bị trùng hoàn toàn.

---

## 7. Lệnh 2 - So sánh `high1` với `Dataset_relabel`

Lệnh này kiểm tra ảnh trong `high1` có đã tồn tại trong dataset cũ chưa:

```bash
python find_duplicate.py --source high1 --source-label high --compare-root Dataset_relabel --out duplicate_report_high1 --mode exact
```

Sau khi chạy xong, kiểm tra file:

```text
duplicate_report_high1/high1_vs_dataset_relabel.csv
```

---

## 8. Lệnh 3 - Bắt ảnh gần giống bằng `aHash`

Chỉ dùng lệnh này nếu đã cài được Pillow.

```bash
python find_duplicate.py --source high1 --source-label high --compare-root Dataset_relabel --out duplicate_report_high1 --mode both --ahash-threshold 3
```

Ý nghĩa:

```text
--ahash-threshold 3
```

là chỉ bắt các ảnh rất gần giống nhau.

Không nên để quá cao vì ảnh ngập nước thường có bối cảnh giống nhau, dễ bị bắt nhầm.

---

## 9. Ý nghĩa các file report

Sau khi chạy, folder `duplicate_report_high1` sẽ có các file:

```text
duplicate_report_high1/
├── image_manifest.csv
├── duplicates_inside_high1.csv
└── high1_vs_dataset_relabel.csv
```

### 9.1. `image_manifest.csv`

Chứa danh sách toàn bộ ảnh đã scan.

Các cột thường gặp:

| Cột         | Ý nghĩa                                                             |
| ----------- | ------------------------------------------------------------------- |
| `path`      | Đường dẫn ảnh                                                       |
| `filename`  | Tên file ảnh                                                        |
| `label`     | Label dự kiến                                                       |
| `origin`    | Ảnh thuộc `source` hay `compare_dataset`                            |
| `file_size` | Dung lượng ảnh                                                      |
| `sha256`    | Hash dùng để tìm ảnh trùng hoàn toàn                                |
| `ahash`     | Hash dùng để tìm ảnh gần giống, chỉ có khi chạy `ahash` hoặc `both` |

---

### 9.2. `duplicates_inside_high1.csv`

Chứa danh sách ảnh duplicate bên trong `high1`.

Các cột quan trọng:

| Cột              | Ý nghĩa                                     |
| ---------------- | ------------------------------------------- |
| `duplicate_type` | Loại duplicate                              |
| `match_type`     | `sha256` hoặc `ahash`                       |
| `keep_path`      | Ảnh nên giữ lại                             |
| `duplicate_path` | Ảnh nghi là trùng, có thể move ra ngoài     |
| `hash_distance`  | Độ khác nhau giữa 2 ảnh, chỉ có với `ahash` |
| `note`           | Ghi chú                                     |

---

### 9.3. `high1_vs_dataset_relabel.csv`

Chứa kết quả so sánh ảnh trong `high1` với `Dataset_relabel`.

Các loại kết quả quan trọng:

| `duplicate_type`                  | Ý nghĩa                                                   |
| --------------------------------- | --------------------------------------------------------- |
| `already_exists_same_label`       | Ảnh trong `high1` đã tồn tại trong `Dataset_relabel/high` |
| `already_exists_same_label_ahash` | Ảnh gần giống đã tồn tại trong `Dataset_relabel/high`     |
| `cross_label_exact_conflict`      | Cùng một ảnh nhưng nằm ở label khác                       |
| `cross_label_ahash_conflict`      | Ảnh gần giống nằm ở label khác                            |

---

## 10. Move duplicate bên trong `high1`

Chỉ chạy sau khi đã kiểm tra file:

```text
duplicate_report_high1/duplicates_inside_high1.csv
```

Lệnh move:

```bash
python find_duplicate.py --source high1 --source-label high --out duplicate_report_high1 --mode exact --move-inside-duplicates
```

Ảnh bị move sẽ nằm ở:

```text
duplicate_report_high1/quarantine/inside_high1_duplicates/
```

Script không xoá vĩnh viễn ảnh, chỉ chuyển ảnh ra khỏi `high1`.

---

## 11. Move ảnh đã tồn tại trong đúng label

Trường hợp ảnh trong `high1` đã tồn tại ở:

```text
Dataset_relabel/high/
```

thì có thể move ra khỏi `high1`.

Lệnh:

```bash
python find_duplicate.py --source high1 --source-label high --compare-root Dataset_relabel --out duplicate_report_high1 --mode exact --move-already-exists
```

Ảnh bị move sẽ nằm ở:

```text
duplicate_report_high1/quarantine/already_exists_same_label/
```

---

## 12. Move ảnh bị trùng với label khác

Trường hợp ảnh trong `high1` bị trùng với:

```text
Dataset_relabel/low/
Dataset_relabel/medium/
Dataset_relabel/non_flood/
```

thì không nên đưa thẳng vào `high`.

Cần move ra folder riêng để kiểm tra thủ công.

Lệnh:

```bash
python find_duplicate.py --source high1 --source-label high --compare-root Dataset_relabel --out duplicate_report_high1 --mode exact --move-cross-label-conflicts
```

Ảnh bị move sẽ nằm ở:

```text
duplicate_report_high1/quarantine/cross_label_conflicts/
```

---

## 13. Quy trình khuyến nghị

Nên làm theo thứ tự sau.

### Bước 1: Tạo report duplicate bên trong `high1`

```bash
python find_duplicate.py --source high1 --source-label high --out duplicate_report_high1 --mode exact
```

Kiểm tra:

```text
duplicate_report_high1/duplicates_inside_high1.csv
```

---

### Bước 2: Move duplicate bên trong `high1`

```bash
python find_duplicate.py --source high1 --source-label high --out duplicate_report_high1 --mode exact --move-inside-duplicates
```

---

### Bước 3: So sánh `high1` với `Dataset_relabel`

```bash
python find_duplicate.py --source high1 --source-label high --compare-root Dataset_relabel --out duplicate_report_high1 --mode exact
```

Kiểm tra:

```text
duplicate_report_high1/high1_vs_dataset_relabel.csv
```

---

### Bước 4: Move ảnh đã tồn tại trong đúng label

```bash
python find_duplicate.py --source high1 --source-label high --compare-root Dataset_relabel --out duplicate_report_high1 --mode exact --move-already-exists
```

---

### Bước 5: Move ảnh trùng với label khác để kiểm tra lại

```bash
python find_duplicate.py --source high1 --source-label high --compare-root Dataset_relabel --out duplicate_report_high1 --mode exact --move-cross-label-conflicts
```

---

### Bước 6: Chạy thêm kiểm tra ảnh gần giống nếu cần

Cài Pillow:

```bash
python -m pip install --upgrade Pillow
```

Chạy:

```bash
python find_duplicate.py --source high1 --source-label high --compare-root Dataset_relabel --out duplicate_report_high1 --mode both --ahash-threshold 3
```

---

## 14. Ý nghĩa tham số

| Tham số                          | Ý nghĩa                                 |
| -------------------------------- | --------------------------------------- |
| `--source high1`                 | Folder ảnh cần lọc                      |
| `--source-label high`            | Label dự kiến của ảnh trong `high1`     |
| `--compare-root Dataset_relabel` | Dataset đã chia label để so sánh        |
| `--out duplicate_report_high1`   | Folder lưu report                       |
| `--mode exact`                   | Chỉ tìm ảnh trùng hoàn toàn             |
| `--mode both`                    | Tìm cả ảnh trùng hoàn toàn và gần giống |
| `--ahash-threshold 3`            | Ngưỡng bắt ảnh gần giống                |
| `--move-inside-duplicates`       | Move duplicate bên trong `high1`        |
| `--move-already-exists`          | Move ảnh đã có trong đúng label         |
| `--move-cross-label-conflicts`   | Move ảnh trùng với label khác           |

---

## 15. Nên chọn `ahash-threshold` bao nhiêu?

Khuyến nghị:

```text
--ahash-threshold 3
```

Bảng tham khảo:

| Threshold | Ý nghĩa                                      |
| --------- | -------------------------------------------- |
| `0`       | Gần như giống tuyệt đối                      |
| `1-3`     | An toàn, ít bắt nhầm                         |
| `4-6`     | Bắt nhiều ảnh gần giống hơn, cần kiểm tra kỹ |
| `>6`      | Không khuyến nghị                            |

Với dataset flood, không nên để threshold quá cao vì nhiều ảnh đường ngập nhìn giống nhau nhưng không phải duplicate.

---

## 16. Quy tắc kiểm tra label flood thủ công

### `non_flood`

Ảnh không có ngập rõ ràng:

- đường khô
- chỉ mưa nhưng chưa ngập
- mặt đường ướt nhưng không có nước đọng/ngập rõ

### `low`

Ngập nhẹ:

- nước dưới đầu gối
- nước dưới thân dưới xe máy
- nước chưa vượt bánh xe ô tô
- xe vẫn di chuyển tương đối dễ

### `medium`

Ngập trung bình:

- nước khoảng đầu gối hoặc trên đầu gối
- nước tới gần hoặc tới yên xe máy
- nước vượt bánh xe ô tô
- di chuyển khó khăn hơn

### `high`

Ngập nặng:

- nước ngang ngực hoặc cao hơn
- nước vượt tay lái xe máy
- nước tới cửa/kính xe ô tô hoặc gần nóc xe
- phương tiện khó hoặc không thể di chuyển

---

## 17. Sau khi lọc xong thì làm gì?

Sau khi chạy các bước lọc:

1. Mở folder `high1`.
2. Kiểm tra ảnh còn lại.
3. Ảnh còn lại nếu đúng là `high` thì chuyển vào:

```text
Dataset_relabel/high/
```

4. Với ảnh trong:

```text
duplicate_report_high1/quarantine/cross_label_conflicts/
```

cần xem lại thủ công và quyết định label đúng.

---

## 18. Lưu ý quan trọng

Không nên đưa toàn bộ `high1` vào `Dataset_relabel/high` ngay lập tức.

Lý do:

- có thể bị trùng ảnh
- có thể có ảnh đã tồn tại trong dataset
- có thể có ảnh bị sai label
- có thể gây data leakage giữa train/val/test
- model dễ học thuộc ảnh duplicate
- kết quả validation/test có thể bị ảo

Nên ưu tiên quy trình:

```text
Report trước → kiểm tra CSV → move vào quarantine → kiểm tra thủ công → mới merge vào Dataset_relabel/high
```

---

## 19. Gợi ý xử lý lỗi cài thư viện trên Windows/MSYS2

Nếu gặp lỗi kiểu:

```text
ERROR: Failed building wheel for cmake
ERROR: Failed to build numpy
ERROR: Failed to build pandas
SSL: CERTIFICATE_VERIFY_FAILED
```

Không cần cài `pandas` nữa.

Dùng script:

```text
find_duplicate_images_no_pandas.py
```

và chạy:

```bash
python find_duplicate_images_no_pandas.py --source high1 --source-label high --out duplicate_report_high1 --mode exact
```

Nếu vẫn muốn dùng ảnh gần giống, chỉ cần cài Pillow:

```bash
python -m pip install --upgrade Pillow
```

Nếu lệnh `python` bị trỏ vào MSYS2 Python và tiếp tục lỗi, nên dùng Python chính thức trên Windows hoặc Anaconda/Miniconda.

Kiểm tra Python đang dùng:

```bash
where python
python --version
python -m pip --version
```

Nếu thấy đường dẫn dạng:

```text
C:\msys64\mingw64\...
```

thì có thể đang dùng Python của MSYS2.

# Cách tạo môi trường ảo đúng trên Windows

Mở terminal trong folder DATA, chạy:

```
py -m venv .venv
```

Kích hoạt môi trường ảo:

```
.venv\Scripts\activate
```

Sau khi activate, kiểm tra Python:

```
where python
python --version
```

Đường dẫn nên là dạng:

`...\DATA\.venv\Scripts\python.exe`
