"""Look up Irish Wikidata labels and aliases for OEWN synsets with Wikidata links.

Writes build/wikidata.tsv: ili, lemma, qid
"""
import dbm
import json

from common import BUILD, WIKIDATA_DB, norm, read_tsv, write_tsv


def main():
    db = dbm.open(str(WIKIDATA_DB), "r")
    rows, linked, found = set(), 0, 0
    for r in read_tsv(BUILD / "oewn.tsv"):
        for qid in r["wikidata"].split():
            linked += 1
            try:
                entity = json.loads(db[qid.encode()])
            except KeyError:
                continue  # no Irish label
            found += 1
            for label in entity["labels"]:
                if label.strip():
                    rows.add((r["ili"], norm(label), qid))
    print(f"Wikidata: {found}/{linked} linked items have an Irish label")
    write_tsv(BUILD / "wikidata.tsv", ["ili", "lemma", "qid"], sorted(rows))


if __name__ == "__main__":
    main()
