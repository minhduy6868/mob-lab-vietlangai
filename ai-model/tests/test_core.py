from pathlib import Path

import pytest

from app.detect import detect_language
from app.translate import Glossary, RouteNotReady, Translator, builtin_glossary, plan_route
from training.validate_pairs import PairFileError, validate_pairs

ROOT = Path(__file__).resolve().parents[1]


def test_catalog_contains_the_five_languages():
    from app.catalog import ethnic_codes

    assert ethnic_codes() == ["tyz", "rad", "cjm", "hmn", "jra"]


def test_direct_glossary_translation():
    result = Translator(builtin_glossary()).translate("Xin chào", "vi", "en")
    assert result["text"] == "Hello"
    assert result["route"] == "direct"
    assert result["engine"] == "glossary"


def test_pivot_uses_vietnamese_when_both_hops_exist():
    glossary = Glossary(
        {
            ("tyz", "vi"): {"pair_a": "xin chào"},
            ("vi", "en"): {"xin chào": "Hello"},
        }
    )
    result = Translator(glossary).translate("pair_a", "tyz", "en")
    assert result["text"] == "Hello"
    assert result["route"] == "pivot"
    assert [step["target"] for step in result["steps"]] == ["vi", "en"]


def test_ethnic_direction_is_not_invented():
    with pytest.raises(RouteNotReady):
        Translator(builtin_glossary()).translate("xin chào", "vi", "tyz")


def test_plan_route_identity_and_direct():
    assert plan_route("vi", "vi", set()) == []
    assert plan_route("vi", "en", {("vi", "en")}) == [("vi", "en")]


def test_detect_cham_script_vietnamese_and_unknown_latin():
    assert detect_language("ꨀꨁ")["language"] == "cjm"
    assert detect_language("Xin chào các bạn")["language"] == "vi"
    assert detect_language("Hello")["language"] == "en"
    assert detect_language("kơdih")["language"] == "und"


def test_pair_file_rejects_unverified_rows(tmp_path: Path):
    path = tmp_path / "pairs.csv"
    path.write_text(
        "source_lang,target_lang,source,target,verified\ntyz,vi,pair_a,xin chào,false\n",
        encoding="utf-8",
    )
    with pytest.raises(PairFileError):
        validate_pairs(path)


def test_sample_pair_file_dry_run():
    summary = validate_pairs(ROOT / "training" / "sample_vi_en.csv")
    assert summary["rows"] == 2
    assert summary["pairs"]["vi->en"] == 1
