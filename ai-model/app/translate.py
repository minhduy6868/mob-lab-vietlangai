import csv
from dataclasses import dataclass, field

from app.catalog import ethnic_codes, language_by_code
from app.detect import detect_language
from app.paths import reviewed_pairs_path


class RouteNotReady(Exception):
    def __init__(self, source: str, target: str) -> None:
        self.source = source
        self.target = target
        super().__init__(f"No reviewed translator for {source} -> {target}")


class UnknownLanguage(Exception):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def normalize(text: str) -> str:
    return " ".join(text.casefold().split())


@dataclass
class Glossary:
    pairs: dict[tuple[str, str], dict[str, str]] = field(default_factory=dict)

    def direct_pairs(self) -> set[tuple[str, str]]:
        return {pair for pair, table in self.pairs.items() if table}

    def translate(self, text: str, source: str, target: str) -> str | None:
        return self.pairs.get((source, target), {}).get(normalize(text))


def builtin_glossary() -> Glossary:
    return Glossary(
        {
            ("vi", "en"): {
                "xin chào": "Hello",
                "cảm ơn": "Thank you",
                "tạm biệt": "Goodbye",
            },
            ("en", "vi"): {
                "hello": "Xin chào",
                "thank you": "Cảm ơn",
                "goodbye": "Tạm biệt",
            },
        }
    )


def load_glossary() -> Glossary:
    glossary = builtin_glossary()
    path = reviewed_pairs_path()
    if not path.is_file():
        return glossary
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            verified = (row.get("verified") or "true").strip().lower()
            if verified not in {"1", "true", "yes"}:
                continue
            pair = (row["source_lang"].strip(), row["target_lang"].strip())
            glossary.pairs.setdefault(pair, {})
            glossary.pairs[pair][normalize(row["source"])] = row["target"].strip()
    return glossary


def plan_route(source: str, target: str, direct: set[tuple[str, str]]) -> list[tuple[str, str]]:
    if source == target:
        return []
    if (source, target) in direct:
        return [(source, target)]
    if (
        source != "vi"
        and target != "vi"
        and (source, "vi") in direct
        and ("vi", target) in direct
    ):
        return [(source, "vi"), ("vi", target)]
    raise RouteNotReady(source, target)


class NeuralEngine:
    """Optional mT5 or NLLB adapter. The glossary stays in front of it."""

    def __init__(self, kind: str, model_name: str) -> None:
        self.kind = kind
        self.name = kind
        self.model_name = model_name
        self._bundle = None

    def pairs(self) -> set[tuple[str, str]]:
        if self.kind == "nllb":
            return {("vi", "en"), ("en", "vi")}
        pairs: set[tuple[str, str]] = set()
        for code in ethnic_codes():
            pairs.add((code, "vi"))
            pairs.add(("vi", code))
        return pairs

    def translate(self, text: str, source: str, target: str) -> str:
        model, tokenizer = self._load()
        if self.kind == "nllb":
            languages = language_by_code()
            tokenizer.src_lang = languages[source]["nllb_code"]
            inputs = tokenizer(text, return_tensors="pt")
            forced = tokenizer.convert_tokens_to_ids(languages[target]["nllb_code"])
            output = model.generate(**inputs, forced_bos_token_id=forced, max_new_tokens=128)
            return tokenizer.batch_decode(output, skip_special_tokens=True)[0]
        prefixed = f"{source} {target}: {text}"
        inputs = tokenizer(prefixed, return_tensors="pt", truncation=True, max_length=128)
        output = model.generate(**inputs, max_new_tokens=128)
        return tokenizer.batch_decode(output, skip_special_tokens=True)[0]

    def _load(self):
        if self._bundle is None:
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            self._bundle = (model, tokenizer)
        return self._bundle


class Translator:
    def __init__(self, glossary: Glossary, neural: NeuralEngine | None = None) -> None:
        self.glossary = glossary
        self.neural = neural
        self.codes = set(language_by_code())

    def direct_pairs(self) -> set[tuple[str, str]]:
        pairs = set(self.glossary.direct_pairs())
        if self.neural is not None:
            pairs |= self.neural.pairs()
        return pairs

    def translate(self, text: str, source: str, target: str) -> dict:
        cleaned = " ".join(text.split())
        if not cleaned:
            raise ValueError("empty")
        detected = None
        if source == "auto":
            found = detect_language(cleaned)
            detected = found["language"]
            if detected == "und":
                raise RouteNotReady("und", target)
            source = detected
        if source not in self.codes or target not in self.codes:
            missing = source if source not in self.codes else target
            raise UnknownLanguage(missing)
        planned = plan_route(source, target, self.direct_pairs())
        current = cleaned
        steps = []
        for step_source, step_target in planned:
            hit = self.glossary.translate(current, step_source, step_target)
            if hit is not None:
                current = hit
                engine = "glossary"
            elif self.neural is not None and (step_source, step_target) in self.neural.pairs():
                current = self.neural.translate(current, step_source, step_target)
                engine = self.neural.name
            else:
                raise RouteNotReady(step_source, step_target)
            steps.append(
                {
                    "source": step_source,
                    "target": step_target,
                    "engine": engine,
                    "text": current,
                }
            )
        route = "direct" if len(planned) == 1 else "pivot"
        if not planned:
            route = "identity"
        engines = [step["engine"] for step in steps]
        return {
            "text": current,
            "source_lang": source,
            "target_lang": target,
            "detected_lang": detected,
            "route": route,
            "engine": "+".join(engines) if engines else "identity",
            "warnings": [],
            "steps": steps,
        }


def build_translator() -> Translator:
    import os

    kind = os.getenv("ML_MT_ENGINE", "glossary")
    neural = None
    if kind == "mt5":
        neural = NeuralEngine("mt5", os.getenv("ML_MT_MODEL", "google/mt5-small"))
    elif kind == "nllb":
        neural = NeuralEngine("nllb", os.getenv("ML_MT_MODEL", "facebook/nllb-200-distilled-600M"))
    elif kind != "glossary":
        raise ValueError(f"Unknown ML_MT_ENGINE: {kind}")
    return Translator(load_glossary(), neural)
