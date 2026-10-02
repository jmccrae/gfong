"""Combine the sources: accept a lemma for a synset when at least 2 of
{wisteria, lsg, wikidata} agree, and add every Horizon lemma directly.

Writes:
  build/synsets.json        one record per included synset
  build/accepted.tsv        one row per accepted lemma, with its sources
  build/review_sample.csv   200 random accepted (non-Horizon) lemmas to check
  build/stats.txt           coverage figures
"""
import csv
import json
import random
from collections import Counter, defaultdict

from common import BUILD, key, read_tsv, write_tsv

VOTERS = ("lsg", "wikidata", "wisteria")
# Which source's spelling to use when sources agree on a lemma.
FORM_PRIORITY = ("horizon", "lsg", "wikidata", "wisteria")


def choose_form(forms, is_instance):
    """forms: {source: form}, all with the same key."""
    ranked = [forms[s] for s in FORM_PRIORITY if s in forms]
    if not is_instance:
        # Wikidata labels are often capitalised; prefer a lower-case spelling
        # for a common noun when any source has one.
        lower = [f for f in ranked if f[:1].islower()]
        if lower:
            return lower[0]
    return ranked[0]


def main():
    oewn = {r["ili"]: r for r in read_tsv(BUILD / "oewn.tsv")}
    instances = {r["source"] for r in read_tsv(BUILD / "oewn_rels.tsv")
                 if r["rel"] == "instance_hypernym"}

    # (ili, key) -> {source: surface form}; ili -> keys in first-seen order
    votes = defaultdict(dict)
    order = defaultdict(dict)
    unknown_ili = Counter()

    def vote(source, ili, lemma):
        if ili not in oewn:
            unknown_ili[source] += 1
            return
        k = key(lemma)
        votes[(ili, k)].setdefault(source, lemma)
        order[ili].setdefault(k, None)

    for r in read_tsv(BUILD / "lsg.tsv"):
        vote("lsg", r["ili"], r["lemma"])
    for r in read_tsv(BUILD / "wikidata.tsv"):
        vote("wikidata", r["ili"], r["lemma"])
    # Wisteria lemmas in descending frequency, so its best lemma comes first.
    for r in sorted(read_tsv(BUILD / "wisteria.tsv"), key=lambda r: -int(r["freq"])):
        vote("wisteria", r["ili"], r["lemma"])
    horizon = {h["ili"]: h for h in json.load(open(BUILD / "horizon.json", encoding="utf-8"))}
    for h in horizon.values():
        for lemma in h["lemmas"]:
            vote("horizon", h["ili"], lemma)

    lsg_defs = {}
    for r in read_tsv(BUILD / "lsg_defs.tsv"):
        lsg_defs.setdefault(r["ili"], r["definition"])

    synsets, accepted = [], []
    pair_counts = Counter()
    for ili, keys in order.items():
        lemmas = []
        # Horizon lemmas first, in the translators' order, then the rest.
        ks = list(keys)
        if ili in horizon:
            hk = [key(l) for l in horizon[ili]["lemmas"]]
            ks = hk + [k for k in ks if k not in hk]
        for k in ks:
            forms = votes[(ili, k)]
            voters = [s for s in VOTERS if s in forms]
            if len(voters) >= 2:
                pair_counts["+".join(voters)] += 1
            if len(voters) >= 2 or "horizon" in forms:
                assert "horizon" in forms or len(set(voters)) >= 2
                sources = sorted(forms)
                lemmas.append(choose_form(forms, oewn[ili]["synset_id"] in instances))
                accepted.append((ili, oewn[ili]["synset_id"], lemmas[-1], "+".join(sources)))
        if not lemmas:
            continue
        o = oewn[ili]
        if ili in horizon and horizon[ili]["definition"]:
            definition, definition_source, confidence = horizon[ili]["definition"], "horizon", None
        elif ili in lsg_defs:
            definition, definition_source, confidence = lsg_defs[ili], "lsg", None
        else:
            definition, definition_source, confidence = o["en_definition"], "oewn", 0.0
        synsets.append({
            "ili": ili, "synset_id": o["synset_id"], "pos": o["pos"], "lexfile": o["lexfile"],
            "lemmas": lemmas, "definition": definition, "definition_source": definition_source,
            "definition_confidence": confidence,
            "example": horizon[ili]["example"] if ili in horizon else "",
        })

    # EWE rejects duplicate definitions. Two synsets given the same Irish gloss
    # (e.g. by LSG) keep the English one, scored 0.0, on all but the first.
    seen = {}
    for s in synsets:
        if s["definition"] in seen:
            print(f"duplicate definition for {seen[s['definition']]} and {s['synset_id']}: "
                  f"{s['definition']!r}")
            s["definition"] = oewn[s["ili"]]["en_definition"]
            s["definition_source"], s["definition_confidence"] = "oewn", 0.0
        seen.setdefault(s["definition"], s["synset_id"])

    with open(BUILD / "synsets.json", "w", encoding="utf-8") as f:
        json.dump(synsets, f, ensure_ascii=False, indent=1)
    write_tsv(BUILD / "accepted.tsv", ["ili", "synset_id", "lemma", "sources"], accepted)

    rng = random.Random(42)
    voted = [a for a in accepted if "horizon" not in a[3]]
    with open(BUILD / "review_sample.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["synset_id", "lemma", "sources", "en_members", "en_definition", "correct?"])
        for ili, ssid, lemma, sources in rng.sample(voted, min(200, len(voted))):
            w.writerow([ssid, lemma, sources, oewn[ili]["en_members"].replace("|", ", "),
                        oewn[ili]["en_definition"], ""])

    by_pos = Counter(s["pos"] for s in synsets)
    by_def = Counter(s["definition_source"] for s in synsets)
    with open(BUILD / "stats.txt", "w", encoding="utf-8") as f:
        print(f"synsets: {len(synsets)}  lemmas (senses): {len(accepted)}", file=f)
        print(f"synsets by POS: {dict(sorted(by_pos.items()))}", file=f)
        print(f"definitions by source: {dict(by_def)}", file=f)
        print(f"lemmas accepted by 2+ voters, by agreeing voters: {dict(pair_counts)}", file=f)
        print(f"lemmas from horizon only: "
              f"{sum(1 for a in accepted if a[3] == 'horizon')}", file=f)
        print(f"candidates dropped for an ILI not in OEWN: {dict(unknown_ili)}", file=f)
    print(open(BUILD / "stats.txt").read())


if __name__ == "__main__":
    main()
