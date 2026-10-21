import csv
from pathlib import Path


REQUIRED = ("source_lang", "target_lang", "source", "target")


class PairFileError(Exception):
    pass


def validate_pairs(path: Path, *, allow_unverified: bool = False) -> dict:
    """Accept only a reviewed parallel CSV.

    Columns: source_lang, target_lang, source, target, verified.
    Training refuses rows that are not marked verified.
    """
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or any(name not in reader.fieldnames for name in REQUIRED):
            raise PairFileError(f"CSV phải có các cột {', '.join(REQUIRED)}")
        if "verified" not in reader.fieldnames and not allow_unverified:
            raise PairFileError("Thiếu cột verified. Không huấn luyện trên câu chưa rà soát.")
        counts: dict[tuple[str, str], int] = {}
        rows = 0
        for line_no, row in enumerate(reader, start=2):
            if not allow_unverified and (row.get("verified") or "").strip().lower() not in {
                "1",
                "true",
                "yes",
            }:
                raise PairFileError(f"Dòng {line_no} chưa được đánh dấu verified.")
            if not row["source"].strip() or not row["target"].strip():
                raise PairFileError(f"Dòng {line_no} thiếu câu nguồn hoặc câu đích.")
            key = (row["source_lang"].strip(), row["target_lang"].strip())
            counts[key] = counts.get(key, 0) + 1
            rows += 1
    if rows == 0:
        raise PairFileError("CSV không có dòng dữ liệu.")
    return {"rows": rows, "pairs": {f"{src}->{tgt}": count for (src, tgt), count in counts.items()}}
