"""Extract the corpus-derived translations from Wisteria's 06_define.json.

Every ranked lemma (up to 5 per synset, count >= 2) is a candidate. Synsets
are keyed by ILI; the few Wisteria synsets without one fall back to their
OEWN synset id, which is mapped to an ILI through build/oewn.tsv.

Writes build/wisteria.tsv: ili, lemma, freq
"""
import json

from common import BUILD, WISTERIA_JSON, norm, read_tsv, write_tsv


def main():
    id_to_ili = {r["synset_id"]: r["ili"] for r in read_tsv(BUILD / "oewn.tsv")}
    rows, missing = [], 0
    for ss in json.load(open(WISTERIA_JSON, encoding="utf-8")):
        ili = ss.get("ili") or id_to_ili.get(ss["synset_id"].removeprefix("oewn-"))
        if not ili:
            missing += 1
            continue
        for lemma, freq in zip(ss["lemmas"], ss["frequencies"]):
            rows.append((ili, norm(lemma), freq))
    print(f"Wisteria: {missing} synsets dropped (no ILI)")
    write_tsv(BUILD / "wisteria.tsv", ["ili", "lemma", "freq"], rows)


if __name__ == "__main__":
    main()
