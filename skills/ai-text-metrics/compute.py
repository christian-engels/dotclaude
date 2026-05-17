#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "textstat>=0.7.4",
#     "nltk>=3.9",
#     "lexical-diversity>=0.1.1",
#     "pypdf>=5.0",
#     "setuptools<81",
# ]
# ///
"""Extract text from a .tex or .pdf and compute AI-text metrics.

Implements the metrics from:
  - Walther & Dutordoir (2025), SSRN 5317993
  - Liang et al. (2024), arXiv 2403.07183

Usage:
    uv run --script compute.py /absolute/path/to/paper.{tex,pdf,txt}
"""
from __future__ import annotations

import json
import re
import string
import sys
from pathlib import Path

import textstat
from lexical_diversity import lex_div
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize

SKILL_DIR = Path(__file__).resolve().parent
WORD_LIST_DIR = SKILL_DIR / "word_lists"

_STEMMER = PorterStemmer()
_PUNCT = str.maketrans("", "", string.punctuation)


def _ensure_nltk() -> None:
    import nltk
    for pkg in ("punkt", "punkt_tab"):
        try:
            nltk.data.find(f"tokenizers/{pkg}")
        except LookupError:
            nltk.download(pkg, quiet=True)


# --- text extraction --------------------------------------------------------

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
    """Crude LaTeX -> plain-text stripping suitable for word-frequency analysis."""
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
        text = re.sub(
            rf"\\{cmd}\*?(?:\[[^\]]*\])?\{{[^}}]*\}}", " ", text,
        )
    # Strip remaining commands but keep argument text (one nesting level).
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


# --- preprocessing & word lists --------------------------------------------

def _tokens_lower(text: str) -> list[str]:
    cleaned = text.lower().translate(_PUNCT)
    return [t for t in word_tokenize(cleaned) if t.isalpha()]


def _tokens_stemmed(text: str) -> list[str]:
    return [_STEMMER.stem(t) for t in _tokens_lower(text)]


def _read_lines(path: Path) -> list[str]:
    return [
        line.strip().lower()
        for line in path.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]


def _ai_density(tokens: list[str], words: set[str]) -> float:
    if not tokens:
        return 0.0
    return sum(1 for t in tokens if t in words) / len(tokens)


# --- metric driver ---------------------------------------------------------

def compute(text: str) -> dict[str, float | int]:
    wd_lines = _read_lines(WORD_LIST_DIR / "walther_dutordoir_22_roots.txt")
    wd_10 = set(wd_lines[:10])
    wd_22 = set(wd_lines)
    liang_200 = (
        set(_read_lines(WORD_LIST_DIR / "liang_2024_adjectives_100.txt"))
        | set(_read_lines(WORD_LIST_DIR / "liang_2024_adverbs_100.txt"))
    )

    n_words = textstat.lexicon_count(text, removepunct=True)
    n_sent = max(textstat.sentence_count(text), 1)
    n_syl = textstat.syllable_count(text)
    toks_lower = _tokens_lower(text)
    toks_stem = [_STEMMER.stem(t) for t in toks_lower]
    n_complex = sum(1 for t in toks_lower if textstat.syllable_count(t) >= 3)

    return {
        "n_words": n_words,
        "n_sentences": n_sent,
        "FKI": textstat.flesch_kincaid_grade(text),
        "GFI": textstat.gunning_fog(text),
        "W_per_S": n_words / n_sent,
        "Syl_per_W": n_syl / max(n_words, 1),
        "CW_per_W": n_complex / max(len(toks_lower), 1),
        "AI_words_10": _ai_density(toks_stem, wd_10),
        "AI_words_22": _ai_density(toks_stem, wd_22),
        "AI_words_200": _ai_density(toks_lower, liang_200),
        "TTR": lex_div.ttr(toks_lower) if toks_lower else 0.0,
        "MTLD": lex_div.mtld(toks_lower) if toks_lower else 0.0,
    }


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: compute.py <path-to-tex-or-pdf>", file=sys.stderr)
        return 2
    _ensure_nltk()
    path = Path(argv[1]).resolve()
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 1
    text = extract_text(path)
    out: dict[str, object] = {"source": str(path), **compute(text)}
    out["preview"] = " ".join(text.split()[:60]) + (" …" if len(text.split()) > 60 else "")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
