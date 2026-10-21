import json
from functools import lru_cache

from app.paths import catalog_path


@lru_cache
def load_catalog() -> dict:
    return json.loads(catalog_path().read_text(encoding="utf-8"))


def language_by_code() -> dict[str, dict]:
    return {row["code"]: row for row in load_catalog()["languages"]}


def ethnic_codes() -> list[str]:
    return [row["code"] for row in load_catalog()["languages"] if row["role"] == "ethnic"]
