"""Extract the OEWN pivot table and its taxonomy from the OEWN YAML source.

Writes:
  build/oewn.tsv        one row per OEWN synset with an ILI
  build/oewn_rels.tsv   hypernym, instance_hypernym and similar edges of every
                        synset, including those without an ILI
"""
import yaml

from common import BUILD, OEWN_YAML, norm, write_tsv

RELS = ("hypernym", "instance_hypernym", "similar")


def as_list(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def main():
    synsets, rels = [], []
    for path in sorted(OEWN_YAML.glob("*.yaml")):
        lexfile = path.stem
        if not lexfile.split(".")[0] in ("noun", "verb", "adj", "adv"):
            continue
        with open(path, encoding="utf-8") as f:
            data = yaml.load(f, Loader=yaml.CSafeLoader)
        for ssid, ss in (data or {}).items():
            for rel in RELS:
                for target in as_list(ss.get(rel)):
                    if isinstance(target, dict):  # scored relation
                        target = target["target"]
                    rels.append((ssid, rel, target))
            ili = ss.get("ili", "")
            if not ili or ili == "in":
                continue
            synsets.append((
                ili, ssid, ss["partOfSpeech"], lexfile,
                " ".join(str(q) for q in as_list(ss.get("wikidata"))),
                "|".join(str(m) for m in ss.get("members", [])),
                norm(as_list(ss.get("definition"))[0]) if ss.get("definition") else "",
            ))
    write_tsv(BUILD / "oewn.tsv",
              ["ili", "synset_id", "pos", "lexfile", "wikidata", "en_members", "en_definition"],
              synsets)
    write_tsv(BUILD / "oewn_rels.tsv", ["source", "rel", "target"], rels)


if __name__ == "__main__":
    main()
