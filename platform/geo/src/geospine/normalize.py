"""Nigerian place-name normalisation.

Two functions:
  norm_name(s)  -> a cleaned, human-readable canonical form ("Aba North")
  name_key(s)   -> an aggressive lookup key for exact/blocked matching
                   ("abanorth"; drops separators and noise words)

Plus SPELLING: a small hand-curated map of Nigeria-specific equivalences that
show up across DHS / MICS / DHIS2 / NBS coding of the same unit.
"""

from __future__ import annotations

import re
import unicodedata

# Whole-token spelling equivalences. Applied after tokenisation, before joining.
# Left side is what may appear upstream; right side is the OCHA COD spelling.
SPELLING: dict[str, str] = {
    "nassarawa": "nasarawa",     # Nasarawa the STATE (not Nassarawa LGA in Kano)
    "cross-river": "cross river",
    "akwaibom": "akwa ibom",
    "fct": "federal capital territory",
    "abuja": "federal capital territory",
    "fct,": "federal capital territory",
    "fct abuja": "federal capital territory",
    "abuja fct": "federal capital territory",
    "abuja municipal": "abuja municipal area council",
    "amac": "abuja municipal area council",
    "municipal area council": "abuja municipal area council",
    "n/central": "north central",
    "n/east": "north east",
    "n/west": "north west",
    "s/east": "south east",
    "s/south": "south south",
    "s/west": "south west",
}

# Noise tokens stripped from name_key() (never from norm_name()).
NOISE = {
    "local", "government", "area", "council", "lga", "l.g.a", "lg",
    "state", "province", "district", "region", "zone", "the",
}

_ROMAN = {
    "i": "1", "ii": "2", "iii": "3", "iv": "4", "v": "5",
    "vi": "6", "vii": "7", "viii": "8", "ix": "9", "x": "10",
}

_WS = re.compile(r"\s+")
_PUNCT = re.compile(r"[.’'`]")           # drop periods and apostrophes
_SEP = re.compile(r"[/\\,;|]+")                # slashes/commas -> space
_NONWORD = re.compile(r"[^a-z0-9\s-]")         # keep letters, digits, space, hyphen


def _strip_accents(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)
    )


def _base(s: str) -> str:
    s = _strip_accents(str(s)).lower().strip()
    s = _PUNCT.sub("", s)
    s = _SEP.sub(" ", s)
    s = _NONWORD.sub(" ", s)
    s = _WS.sub(" ", s).strip()
    # phrase-level spelling fixes first (multi-word keys)
    for bad, good in SPELLING.items():
        if " " in bad:
            s = re.sub(rf"\b{re.escape(bad)}\b", good, s)
    return s


def norm_name(s: str) -> str:
    """Cleaned, display-ready canonical form. Keeps word order and directions."""
    s = _base(s)
    toks = []
    for t in s.split():
        t = SPELLING.get(t, t)
        toks.append(t)
    s = " ".join(toks)
    s = _WS.sub(" ", s).strip()
    return s.title() if s else s


def name_key(s: str) -> str:
    """Aggressive key: no separators (incl. hyphens), no noise words,
    roman numerals -> digits. 'Sabon-Gari' == 'Sabon Gari' == 'sabongari'."""
    s = _base(s).replace("-", " ")
    toks = []
    for t in s.split():
        t = SPELLING.get(t, t)  # may expand to a multi-word string (fct -> ...)
        for w in t.replace("-", " ").split():
            if w in NOISE:
                continue
            toks.append(_ROMAN.get(w, w))
    return "".join(toks)
