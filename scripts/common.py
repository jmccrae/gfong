"""Shared paths and helpers for the GréasánFocal build scripts."""
import csv
import os
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
HOME = Path.home()

OEWN_YAML = Path(os.environ.get(
    "OEWN_YAML", HOME / "projects/globalwordnet/english-wordnet/src/yaml"))
LSG_XML = ROOT / "lsg-lmf.xml"
WISTERIA_JSON = Path(os.environ.get(
    "WISTERIA_JSON",
    HOME / "projects/jmccrae/wisteria/irish/out-glossbert/work/06_define.json"))
WIKIDATA_DB = Path(os.environ.get(
    "WIKIDATA_DB", HOME / "projects/jmccrae/linkingtk/wikidata_index_ga/entities.db"))
HORIZON_TXT = ROOT / "horizon_translations" / "gfong_Horizon Translations_Adapt_TRA.txt"

_APOSTROPHES = str.maketrans({"’": "'", "‘": "'", "ʼ": "'", "`": "'"})


def norm(text):
    """Normalise a lemma or gloss: NFC, straight apostrophes, single spaces."""
    text = unicodedata.normalize("NFC", text).translate(_APOSTROPHES)
    return re.sub(r"\s+", " ", text).strip()


def key(lemma):
    """Matching key for a lemma: the casefolded normal form. Fadas and initial
    mutations are kept, as they distinguish Irish words."""
    return norm(lemma).casefold()


def write_tsv(path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
        w.writerow(header)
        n = 0
        for row in rows:
            w.writerow(row)
            n += 1
    print(f"wrote {n} rows to {path.relative_to(ROOT)}")


def read_tsv(path):
    with open(path, newline="", encoding="utf-8") as f:
        yield from csv.DictReader(f, delimiter="\t")
