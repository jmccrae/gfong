"""Write the EWE automaton script that builds the wordnet.

All synsets are added first, then all relations, so every relation target
exists when it is added. Definitions with no Irish source are the OEWN
English gloss, with definition_confidence 0.0.

Writes build/automaton.yaml
"""
import json

import yaml

from common import BUILD, read_tsv


def main():
    synsets = json.load(open(BUILD / "synsets.json", encoding="utf-8"))
    demoted = {r["synset_id"]: r["new_id"] for r in read_tsv(BUILD / "demoted.tsv")}
    actions = []
    for s in synsets:
        ssid = demoted.get(s["synset_id"], s["synset_id"])
        add = {
            "id": ssid,
            "ili": s["ili"],
            "definition": s["definition"],
            "lexfile": s["lexfile"],
            "pos": ssid[-1],
            "lemmas": s["lemmas"],
        }
        if s["definition_confidence"] is not None:
            add["definition_confidence"] = s["definition_confidence"]
        actions.append({"add_synset": add})
        if s["example"]:
            actions.append({"add_example": {"synset": ssid, "example": s["example"]}})
    for r in read_tsv(BUILD / "relations.tsv"):
        actions.append({"add_relation": {
            "source": demoted.get(r["source"], r["source"]),
            "relation": r["rel"],
            "target": demoted.get(r["target"], r["target"]),
        }})
    actions.append("validate")
    with open(BUILD / "automaton.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(actions, f, allow_unicode=True, sort_keys=False, width=1000)
    print(f"wrote {len(actions)} actions to build/automaton.yaml")


if __name__ == "__main__":
    main()
