"""Project OEWN's taxonomy onto the included synsets.

Each included noun or verb gets as hypernyms its nearest included ancestors
in OEWN, skipping over synsets not (yet) included. A candidate that is itself
an ancestor of another candidate is dropped, as the relation would be
redundant. Synsets whose OEWN hypernyms are all instance_hypernym links keep
that relation type.

Satellite adjectives keep their `similar` link to their head when the head is
included; otherwise they are made head adjectives (POS `a`).

Writes:
  build/relations.tsv   source, rel, target
  build/demoted.tsv     satellites made head adjectives
"""
import json
from collections import Counter, defaultdict
from functools import lru_cache

from common import BUILD, read_tsv, write_tsv

ROOT = "00001740-n"


def main():
    synsets = json.load(open(BUILD / "synsets.json", encoding="utf-8"))
    included = {s["synset_id"] for s in synsets}
    if ROOT not in included:
        raise SystemExit(f"{ROOT} (entity) has no Irish lemma; every noun needs it as a root")

    parents = defaultdict(list)  # synset -> [(rel, target)]
    similar = defaultdict(list)
    for r in read_tsv(BUILD / "oewn_rels.tsv"):
        if r["rel"] == "similar":
            similar[r["source"]].append(r["target"])
        else:
            parents[r["source"]].append((r["rel"], r["target"]))

    @lru_cache(maxsize=None)
    def ancestors(ssid):
        out = set()
        for _, target in parents[ssid]:
            out.add(target)
            out |= ancestors(target)
        return frozenset(out)

    def nearest_included(ssid):
        found, seen = [], set()
        frontier = [t for _, t in parents[ssid]]
        while frontier:
            nxt = []
            for t in frontier:
                if t in seen:
                    continue
                seen.add(t)
                if t in included:
                    found.append(t)
                else:
                    nxt.extend(t2 for _, t2 in parents[t])
            frontier = nxt
        return [t for t in found if not any(t in ancestors(o) for o in found if o != t)]

    relations, demoted = [], []
    stats = Counter()
    for s in synsets:
        ssid = s["synset_id"]
        if s["pos"] in ("n", "v") and ssid != ROOT:
            rels = {rel for rel, _ in parents[ssid]}
            rel = "instance_hypernym" if rels == {"instance_hypernym"} else "hypernym"
            targets = nearest_included(ssid)
            direct = {t for _, t in parents[ssid]}
            if not targets:
                stats[f"{s['pos']}: no included ancestor"] += 1
            elif set(targets) == direct:
                stats[f"{s['pos']}: direct hypernym"] += 1
            else:
                stats[f"{s['pos']}: skipped to a more distant ancestor"] += 1
            for t in targets:
                relations.append((ssid, rel, t))
        elif s["pos"] == "s":
            heads = [h for h in similar[ssid] if h in included]
            if heads:
                relations.append((ssid, "similar", heads[0]))
                stats["s: similar to included head"] += 1
            else:
                demoted.append((ssid, ssid[:-1] + "a"))
                stats["s: head not included, made a head adjective"] += 1

    nouns_without = [s["synset_id"] for s in synsets if s["pos"] == "n"
                     and s["synset_id"] != ROOT
                     and not any(r[0] == s["synset_id"] for r in relations)]
    assert not nouns_without, f"nouns with no hypernym: {nouns_without[:10]}"
    write_tsv(BUILD / "relations.tsv", ["source", "rel", "target"], relations)
    write_tsv(BUILD / "demoted.tsv", ["synset_id", "new_id"], demoted)
    with open(BUILD / "stats.txt", "a", encoding="utf-8") as f:
        print("taxonomy:", file=f)
        for k, v in sorted(stats.items()):
            print(f"  {k}: {v}", file=f)
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
