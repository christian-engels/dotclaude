#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "nltk>=3.9",
#     "pypdf>=5.0",
# ]
# ///
"""Find every occurrence of an LLM-cliché word or phrase in a .tex/.pdf/.txt
and print it + its sentence context as JSON.

Word lists:
  - Walther & Dutordoir (2025) 10 + 22 stemmed roots  (Porter-stem matching)
  - Liang et al. (2024) 200 unstemmed adjectives + adverbs  (literal matching)
  - Wikipedia "Signs of AI writing" single words       (literal matching)
  - Wikipedia "Signs of AI writing" phrases            (case-insensitive,
    word-boundary substring matching)

Usage:
    uv run --script detect.py /absolute/path/to/paper.{tex,pdf,txt}
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from nltk.stem.porter import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize

SKILL_DIR = Path(__file__).resolve().parent
WORD_LIST_DIR = SKILL_DIR / "word_lists"

_STEMMER = PorterStemmer()


def _ensure_nltk() -> None:
    import nltk
    for pkg in ("punkt", "punkt_tab"):
        try:
            nltk.data.find(f"tokenizers/{pkg}")
        except LookupError:
            nltk.download(pkg, quiet=True)


# --- text extraction (mirrors ai-text-metrics/compute.py) ------------------

_INPUT_RE = re.compile(r"\\(?:input|include|subfile)\s*\{([^}]+)\}")
_COMMENT_RE = re.compile(r"(?<!\\)%.*?$", re.MULTILINE)
_MATH_ENVS = (
    "equation", "align", "eqnarray", "gather", "multline",
    "tabular", "table", "figure", "tikzpicture", "lstlisting",
    "verbatim", "minted", "thebibliography",
)
_DROP_CMDS = (
    "cite", "citep", "citet", "citeauthor", "citeyear", "ref", "label",
    "eqref", "pageref", "footnote", "url", "href", "bibliography",
    "bibliographystyle", "input", "include",
)


def _resolve_tex(path: Path, seen: set[Path] | None = None) -> str:
    seen = set() if seen is None else seen
    if not path.exists() and path.suffix != ".tex":
        path = path.with_suffix(".tex")
    if not path.exists() or path in seen:
        return ""
    seen.add(path)
    text = _COMMENT_RE.sub("", path.read_text(errors="replace"))
    base = path.parent

    def _sub(m: re.Match) -> str:
        sub = base / m.group(1).strip()
        if sub.suffix != ".tex":
            sub = sub.with_suffix(".tex")
        return _resolve_tex(sub, seen)

    return _INPUT_RE.sub(_sub, text)


def _strip_latex(text: str) -> str:
    m = re.search(r"\\begin\{document\}", text)
    if m:
        text = text[m.end():]
    text = re.sub(r"\\end\{document\}.*", "", text, flags=re.DOTALL)
    text = re.sub(r"\$\$.*?\$\$", " ", text, flags=re.DOTALL)
    text = re.sub(r"\$[^$]+\$", " ", text)
    text = re.sub(r"\\\[.*?\\\]", " ", text, flags=re.DOTALL)
    text = re.sub(r"\\\(.*?\\\)", " ", text, flags=re.DOTALL)
    for env in _MATH_ENVS:
        text = re.sub(
            rf"\\begin\{{{env}\*?\}}.*?\\end\{{{env}\*?\}}",
            " ", text, flags=re.DOTALL,
        )
    for cmd in _DROP_CMDS:
        text = re.sub(rf"\\{cmd}\*?(?:\[[^\]]*\])?\{{[^}}]*\}}", " ", text)
    text = re.sub(
        r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?\s*\{([^{}]*)\}", r" \1 ", text,
    )
    text = re.sub(r"\\[a-zA-Z]+\*?", " ", text)
    text = re.sub(r"[{}]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _extract_pdf(path: Path) -> str:
    from pypdf import PdfReader
    reader = PdfReader(str(path))
    return "\n".join((p.extract_text() or "") for p in reader.pages)


def extract_text(path: Path) -> str:
    suf = path.suffix.lower()
    if suf == ".pdf":
        return _extract_pdf(path)
    if suf == ".tex":
        return _strip_latex(_resolve_tex(path))
    return path.read_text()


# --- word-list matching ----------------------------------------------------

def _read_lines(path: Path) -> list[str]:
    return [
        line.strip().lower()
        for line in path.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]


def _load_lists() -> dict[str, set[str] | list[str]]:
    wd_lines = _read_lines(WORD_LIST_DIR / "walther_dutordoir_22_roots.txt")
    return {
        "wd_10": set(wd_lines[:10]),
        "wd_22": set(wd_lines),
        "liang_200": (
            set(_read_lines(WORD_LIST_DIR / "liang_2024_adjectives_100.txt"))
            | set(_read_lines(WORD_LIST_DIR / "liang_2024_adverbs_100.txt"))
        ),
        "wp_words": set(_read_lines(WORD_LIST_DIR / "wikipedia_signs_words.txt")),
        "wp_phrases": _read_lines(WORD_LIST_DIR / "wikipedia_signs_phrases.txt"),
    }


def find_matches(text: str) -> dict:
    lists = _load_lists()
    sentences = sent_tokenize(text)
    matches: list[dict] = []

    for sent_idx, sent in enumerate(sentences):
        compact = " ".join(sent.split())
        for tok in word_tokenize(sent):
            if not tok.isalpha():
                continue
            low = tok.lower()
            stem = _STEMMER.stem(low)
            hit_lists: list[str] = []
            if stem in lists["wd_10"]:
                hit_lists.append("WD-10")
            if stem in lists["wd_22"] and "WD-10" not in hit_lists:
                hit_lists.append("WD-22")
            elif stem in lists["wd_22"]:
                hit_lists.append("WD-22")
            if low in lists["liang_200"]:
                hit_lists.append("Liang-200")
            if low in lists["wp_words"]:
                hit_lists.append("WP-words")
            if hit_lists:
                matches.append({
                    "word": tok,
                    "stem": stem,
                    "lists": hit_lists,
                    "sentence_idx": sent_idx,
                    "context": compact,
                })

        sent_low = compact.lower()
        for phrase in lists["wp_phrases"]:
            for _ in re.finditer(rf"\b{re.escape(phrase)}\b", sent_low):
                matches.append({
                    "word": phrase,
                    "stem": phrase,
                    "lists": ["WP-phrases"],
                    "sentence_idx": sent_idx,
                    "context": compact,
                })

    summary: dict[str, dict] = {}
    for m in matches:
        key = m["word"].lower()
        s = summary.setdefault(key, {"count": 0, "lists": set(), "stem": m["stem"]})
        s["count"] += 1
        s["lists"].update(m["lists"])
    summary_clean = {
        k: {"count": v["count"], "stem": v["stem"], "lists": sorted(v["lists"])}
        for k, v in sorted(summary.items(), key=lambda kv: -kv[1]["count"])
    }

    return {
        "n_sentences": len(sentences),
        "n_matches": len(matches),
        "summary": summary_clean,
        "matches": matches,
    }


def main(argv: list[str]) -> int:
    args = argv[1:]
    prose_out: Path | None = None
    if "--prose-out" in args:
        idx = args.index("--prose-out")
        prose_out = Path(args[idx + 1]).resolve()
        del args[idx:idx + 2]
    if len(args) < 1:
        print(
            "Usage: detect.py <path-to-tex-or-pdf> [--prose-out <path>]",
            file=sys.stderr,
        )
        return 2
    _ensure_nltk()
    path = Path(args[0]).resolve()
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 1
    text = extract_text(path)
    if prose_out is not None:
        prose_out.write_text(text)
    out = {"source": str(path), **find_matches(text)}
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
