import argparse
import csv
import hashlib
import shutil
from pathlib import Path
from collections import defaultdict

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}

try:
    from PIL import Image
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False


def is_image(path: Path) -> bool:
    return path.suffix.lower() in IMAGE_EXTS


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def average_hash(path: Path, hash_size: int = 8):
    """
    Hash ảnh gần giống, không cần numpy/imagehash.
    Cần Pillow. Nếu không cài Pillow thì chỉ dùng được exact hash.
    """
    if not PIL_AVAILABLE:
        return None

    try:
        with Image.open(path) as img:
            img = img.convert("L")

            try:
                resample = Image.Resampling.LANCZOS
            except AttributeError:
                resample = Image.LANCZOS

            img = img.resize((hash_size, hash_size), resample)
            pixels = list(img.getdata())
            avg = sum(pixels) / len(pixels)

            bits = ["1" if p >= avg else "0" for p in pixels]
            return "".join(bits)
    except Exception:
        return None


def hamming_distance(a: str, b: str) -> int:
    if a is None or b is None:
        return 9999
    return sum(x != y for x, y in zip(a, b))


def collect_source_images(source_folder: Path, source_label: str):
    rows = []

    for path in source_folder.rglob("*"):
        if path.is_file() and is_image(path):
            rows.append({
                "path": str(path.resolve()),
                "filename": path.name,
                "label": source_label,
                "origin": "source",
                "file_size": path.stat().st_size,
            })

    return rows


def collect_labeled_dataset(compare_root: Path):
    rows = []

    if compare_root is None:
        return rows

    for label_dir in compare_root.iterdir():
        if not label_dir.is_dir():
            continue

        label = label_dir.name

        for path in label_dir.rglob("*"):
            if path.is_file() and is_image(path):
                rows.append({
                    "path": str(path.resolve()),
                    "filename": path.name,
                    "label": label,
                    "origin": "compare_dataset",
                    "file_size": path.stat().st_size,
                })

    return rows


def write_csv(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)

    rows = list(rows)

    if not rows:
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            f.write("")
        return

    fieldnames = []
    seen = set()

    for row in rows:
        for key in row.keys():
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)

    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def dedupe_rows(rows):
    seen = set()
    output = []

    for row in rows:
        key = tuple(sorted(row.items()))
        if key not in seen:
            seen.add(key)
            output.append(row)

    return output


def safe_move(src: Path, dst_root: Path, base_root: Path):
    try:
        relative = src.relative_to(base_root)
    except ValueError:
        relative = Path(src.name)

    dst = dst_root / relative
    dst.parent.mkdir(parents=True, exist_ok=True)

    if dst.exists():
        stem = dst.stem
        suffix = dst.suffix
        i = 1

        while True:
            candidate = dst.with_name(f"{stem}_dup{i}{suffix}")
            if not candidate.exists():
                dst = candidate
                break
            i += 1

    shutil.move(str(src), str(dst))
    return dst


def report_inside_exact(rows):
    source_rows = [r for r in rows if r["origin"] == "source"]
    groups = defaultdict(list)

    for row in source_rows:
        groups[row["sha256"]].append(row)

    report = []

    for sha, group in groups.items():
        if len(group) <= 1:
            continue

        group = sorted(group, key=lambda r: (-int(r["file_size"]), r["path"]))
        keep = group[0]

        for dup in group[1:]:
            report.append({
                "duplicate_type": "inside_high1_exact_duplicate",
                "match_type": "sha256",
                "hash": sha,
                "keep_path": keep["path"],
                "duplicate_path": dup["path"],
                "label": dup["label"],
                "note": "Ảnh trùng hoàn toàn bên trong folder high1."
            })

    return report


def build_near_duplicate_clusters(records, threshold):
    n = len(records)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for i in range(n):
        if i % 100 == 0:
            print(f"Comparing near duplicates: {i}/{n}")

        for j in range(i + 1, n):
            dist = hamming_distance(records[i].get("ahash"), records[j].get("ahash"))
            if dist <= threshold:
                union(i, j)

    clusters = defaultdict(list)

    for i, row in enumerate(records):
        clusters[find(i)].append(row)

    return [cluster for cluster in clusters.values() if len(cluster) > 1]


def report_inside_ahash(rows, threshold):
    source_rows = [
        r for r in rows
        if r["origin"] == "source" and r.get("ahash")
    ]

    report = []
    clusters = build_near_duplicate_clusters(source_rows, threshold)

    for group in clusters:
        group = sorted(group, key=lambda r: (-int(r["file_size"]), r["path"]))
        keep = group[0]

        for dup in group[1:]:
            dist = hamming_distance(keep.get("ahash"), dup.get("ahash"))
            report.append({
                "duplicate_type": "inside_high1_ahash_duplicate",
                "match_type": "ahash",
                "hash": dup.get("ahash"),
                "hash_distance": dist,
                "keep_path": keep["path"],
                "duplicate_path": dup["path"],
                "label": dup["label"],
                "note": f"Ảnh gần giống bên trong high1. aHash distance <= {threshold}."
            })

    return report


def report_source_vs_dataset_exact(rows, source_label):
    source_rows = [r for r in rows if r["origin"] == "source"]
    compare_rows = [r for r in rows if r["origin"] == "compare_dataset"]

    compare_by_sha = defaultdict(list)

    for row in compare_rows:
        compare_by_sha[row["sha256"]].append(row)

    report = []

    for src in source_rows:
        matches = compare_by_sha.get(src["sha256"], [])

        for match in matches:
            if match["label"] == source_label:
                duplicate_type = "already_exists_same_label"
                note = "Ảnh trong high1 đã tồn tại trong đúng label."
            else:
                duplicate_type = "cross_label_exact_conflict"
                note = "Cùng một ảnh nhưng nằm ở label khác. Cần kiểm tra lại nhãn."

            report.append({
                "duplicate_type": duplicate_type,
                "match_type": "sha256",
                "source_label": source_label,
                "matched_label": match["label"],
                "source_path": src["path"],
                "matched_path": match["path"],
                "note": note
            })

    return report


def report_source_vs_dataset_ahash(rows, source_label, threshold):
    source_rows = [
        r for r in rows
        if r["origin"] == "source" and r.get("ahash")
    ]

    compare_rows = [
        r for r in rows
        if r["origin"] == "compare_dataset" and r.get("ahash")
    ]

    report = []

    for i, src in enumerate(source_rows):
        if i % 50 == 0:
            print(f"Comparing high1 vs dataset: {i}/{len(source_rows)}")

        for cmp_img in compare_rows:
            dist = hamming_distance(src.get("ahash"), cmp_img.get("ahash"))

            if dist <= threshold:
                if cmp_img["label"] == source_label:
                    duplicate_type = "already_exists_same_label_ahash"
                    note = "Ảnh gần giống đã tồn tại trong đúng label."
                else:
                    duplicate_type = "cross_label_ahash_conflict"
                    note = "Ảnh gần giống nằm ở label khác. Cần kiểm tra thủ công."

                report.append({
                    "duplicate_type": duplicate_type,
                    "match_type": "ahash",
                    "hash_distance": dist,
                    "source_label": source_label,
                    "matched_label": cmp_img["label"],
                    "source_path": src["path"],
                    "matched_path": cmp_img["path"],
                    "note": note
                })

    return report


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--source", required=True, help="Folder ảnh cần lọc, ví dụ: high1")
    parser.add_argument("--source-label", default="high", help="Label dự kiến của folder source")
    parser.add_argument("--compare-root", default=None, help="Dataset đã chia label, ví dụ: Dataset_relabel")
    parser.add_argument("--out", default="duplicate_report_high1", help="Folder xuất report")
    parser.add_argument("--mode", choices=["exact", "ahash", "both"], default="both")
    parser.add_argument("--ahash-threshold", type=int, default=3)

    parser.add_argument("--move-inside-duplicates", action="store_true")
    parser.add_argument("--move-already-exists", action="store_true")
    parser.add_argument("--move-cross-label-conflicts", action="store_true")

    args = parser.parse_args()

    source_folder = Path(args.source).resolve()
    compare_root = Path(args.compare_root).resolve() if args.compare_root else None
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not source_folder.exists():
        raise RuntimeError(f"Không tìm thấy source folder: {source_folder}")

    if compare_root is not None and not compare_root.exists():
        raise RuntimeError(f"Không tìm thấy compare root: {compare_root}")

    if args.mode in ["ahash", "both"] and not PIL_AVAILABLE:
        print("WARNING: Chưa cài Pillow, script sẽ chỉ chạy exact hash.")
        print("Cài Pillow bằng lệnh: py -m pip install --upgrade Pillow")
        args.mode = "exact"

    print(f"Source folder: {source_folder}")
    print(f"Source label: {args.source_label}")
    print(f"Compare root: {compare_root}")
    print(f"Output folder: {out_dir}")
    print(f"Mode: {args.mode}")

    rows = collect_source_images(source_folder, args.source_label)

    if compare_root is not None:
        rows.extend(collect_labeled_dataset(compare_root))

    if not rows:
        raise RuntimeError("Không tìm thấy ảnh nào.")

    print(f"Total images found: {len(rows)}")

    for i, row in enumerate(rows):
        if i % 100 == 0:
            print(f"Hashing: {i}/{len(rows)}")

        path = Path(row["path"])
        row["sha256"] = sha256_file(path)

        if args.mode in ["ahash", "both"]:
            row["ahash"] = average_hash(path)
        else:
            row["ahash"] = ""

    manifest_csv = out_dir / "image_manifest.csv"
    write_csv(manifest_csv, rows)

    inside_report = []
    dataset_report = []

    if args.mode in ["exact", "both"]:
        inside_report.extend(report_inside_exact(rows))

        if compare_root is not None:
            dataset_report.extend(report_source_vs_dataset_exact(rows, args.source_label))

    if args.mode in ["ahash", "both"]:
        inside_report.extend(report_inside_ahash(rows, args.ahash_threshold))

        if compare_root is not None:
            dataset_report.extend(
                report_source_vs_dataset_ahash(rows, args.source_label, args.ahash_threshold)
            )

    inside_report = dedupe_rows(inside_report)
    dataset_report = dedupe_rows(dataset_report)

    inside_csv = out_dir / "duplicates_inside_high1.csv"
    compare_csv = out_dir / "high1_vs_dataset_relabel.csv"

    write_csv(inside_csv, inside_report)
    write_csv(compare_csv, dataset_report)

    print()
    print("====== REPORT ======")
    print(f"Total images scanned: {len(rows)}")
    print(f"Inside high1 duplicates: {len(inside_report)}")
    print(f"High1 vs Dataset_relabel matches/conflicts: {len(dataset_report)}")
    print(f"Manifest: {manifest_csv}")
    print(f"Inside duplicates: {inside_csv}")
    print(f"High1 vs dataset report: {compare_csv}")

    quarantine_root = out_dir / "quarantine"

    if args.move_inside_duplicates and inside_report:
        move_dir = quarantine_root / "inside_high1_duplicates"
        moved = []

        paths = sorted(set(row["duplicate_path"] for row in inside_report if row.get("duplicate_path")))

        for path_str in paths:
            src = Path(path_str)
            if src.exists():
                dst = safe_move(src, move_dir, source_folder)
                moved.append({"src": str(src), "dst": str(dst)})

        moved_csv = out_dir / "moved_inside_high1_duplicates.csv"
        write_csv(moved_csv, moved)
        print(f"Moved inside duplicates: {len(moved)}")
        print(f"Move log: {moved_csv}")

    if args.move_already_exists and dataset_report:
        move_dir = quarantine_root / "already_exists_same_label"
        moved = []

        paths = sorted(set(
            row["source_path"]
            for row in dataset_report
            if "already_exists_same_label" in row.get("duplicate_type", "")
        ))

        for path_str in paths:
            src = Path(path_str)
            if src.exists():
                dst = safe_move(src, move_dir, source_folder)
                moved.append({"src": str(src), "dst": str(dst)})

        moved_csv = out_dir / "moved_already_exists_same_label.csv"
        write_csv(moved_csv, moved)
        print(f"Moved already-exists images: {len(moved)}")
        print(f"Move log: {moved_csv}")

    if args.move_cross_label_conflicts and dataset_report:
        move_dir = quarantine_root / "cross_label_conflicts"
        moved = []

        paths = sorted(set(
            row["source_path"]
            for row in dataset_report
            if "cross_label" in row.get("duplicate_type", "")
        ))

        for path_str in paths:
            src = Path(path_str)
            if src.exists():
                dst = safe_move(src, move_dir, source_folder)
                moved.append({"src": str(src), "dst": str(dst)})

        moved_csv = out_dir / "moved_cross_label_conflicts.csv"
        write_csv(moved_csv, moved)
        print(f"Moved cross-label conflicts: {len(moved)}")
        print(f"Move log: {moved_csv}")

    print()
    print("Done.")


if __name__ == "__main__":
    main()
