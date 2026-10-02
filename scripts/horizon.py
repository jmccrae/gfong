"""Parse the Horizon translations and match each item to an OEWN synset.

The file alternates English and Irish records, each a line of comma-separated
lemmas followed by a definition line and an optional example line. The
English records carry no ids, so they are matched to OEWN by definition and
lemma set:

  1. exact   - the normalised definition matches exactly one OEWN synset, or
               the English lemmas pick out one of several matches
  2. fuzzy   - the closest definition (difflib) among OEWN synsets sharing an
               English lemma, if similar enough
  3. lemmas  - the only OEWN synset with exactly the same (2+) English lemmas

Writes:
  build/horizon.json            matched items
  build/horizon_unmatched.tsv   items that need matching by hand
"""
import difflib
import json
import re
from collections import defaultdict

from common import BUILD, HORIZON_TXT, key, norm, read_tsv, write_tsv

EN_DEF = re.compile(r"^Definition\s*[:;]\s*(.*)$")
EN_EX = re.compile(r"^Example\s*[:;]\s*(.*)$")
GA_DEF = re.compile(r"^(?:Sainmhíniú|Míniú|Míníu|Miniú|Mìniú)(?:\s*[:;]\s*|\s+)(.*)$")
GA_EX = re.compile(r"^Sampla\s*[:;]\s*(.*)$")
FUZZY_THRESHOLD = 0.8


def split_lemmas(line):
    seen, lemmas = set(), []
    for lemma in line.split(","):
        lemma = norm(lemma)
        if lemma and key(lemma) not in seen:
            seen.add(key(lemma))
            lemmas.append(lemma)
    return lemmas


def parse():
    """Yield (English record, Irish record) pairs; a record is a dict with
    lemmas, definition and example."""
    records = []
    with open(HORIZON_TXT, encoding="utf-8-sig") as f:
        lines = [norm(l) for l in f]
    for line in lines:
        if not line:
            continue
        for lang, pattern, field in (("en", EN_DEF, "definition"), ("en", EN_EX, "example"),
                                     ("ga", GA_DEF, "definition"), ("ga", GA_EX, "example")):
            m = pattern.match(line)
            if m:
                rec = records[-1]
                if rec.get("lang") not in (None, lang):
                    # A translation with its lemma line missing.
                    print(f"Horizon: no lemma line before: {line}")
                    rec = {"lemmas": [], "definition": "", "example": ""}
                    records.append(rec)
                rec["lang"] = lang
                rec[field] = m.group(1).strip()
                break
        else:
            if records and "lang" not in records[-1]:
                # A definition with its label missing, straight after a lemma line.
                print(f"Horizon: unlabelled definition: {line}")
                records[-1]["lang"] = "ga" if records[-2].get("lang") == "en" else "en"
                records[-1]["definition"] = line
            else:
                records.append({"lemmas": split_lemmas(line), "definition": "", "example": ""})
    # Translations usually follow their English record directly, but some runs
    # of English records are followed by their translations in the same order.
    pairs, pending = [], []
    for rec in records:
        if rec.get("lang") == "en":
            pending.append(rec)
        elif rec.get("lang") == "ga":
            if not pending:
                raise ValueError(f"Translation without an English record: {rec}")
            pairs.append((pending.pop(0), rec))
        else:
            raise ValueError(f"Record with no definition: {rec}")
    if pending:
        raise ValueError(f"English records without a translation: {pending}")
    return pairs


def def_key(text):
    return re.sub(r"[^\w ]", "", norm(text).casefold())


def main():
    oewn = list(read_tsv(BUILD / "oewn.tsv"))
    by_def, by_member = defaultdict(list), defaultdict(list)
    for r in oewn:
        r["members"] = {key(m) for m in r["en_members"].split("|")}
        by_def[def_key(r["en_definition"])].append(r)
        for m in r["members"]:
            by_member[m].append(r)

    matched, unmatched = [], []
    for en, ga in parse():
        en_keys = {key(l) for l in en["lemmas"]}

        def overlap(r):
            return len(en_keys & r["members"]) / len(en_keys | r["members"])

        method, best = None, None
        candidates = by_def.get(def_key(en["definition"]), [])
        if candidates:
            best = max(candidates, key=overlap)
            if len(candidates) == 1 or overlap(best) > 0:
                method = "exact"
        if method is None:
            pool = {r["synset_id"]: r for l in en_keys for r in by_member.get(l, [])}.values()
            scored = [(difflib.SequenceMatcher(None, def_key(en["definition"]),
                                               def_key(r["en_definition"])).ratio(), overlap(r), r)
                      for r in pool]
            if scored:
                ratio, _, best = max(scored, key=lambda t: (t[0], t[1]))
                if ratio >= FUZZY_THRESHOLD:
                    method = "fuzzy"
            if method is None and len(en_keys) > 1:
                same = [r for r in pool if r["members"] == en_keys]
                if len(same) == 1:
                    method, best = "lemmas", same[0]
        if method is None:
            unmatched.append((", ".join(en["lemmas"]), en["definition"], en["example"],
                              ", ".join(ga["lemmas"]), best["synset_id"] if best else ""))
            continue
        matched.append({
            "ili": best["ili"], "synset_id": best["synset_id"], "match": method,
            "en_lemmas": en["lemmas"], "en_definition": en["definition"],
            "lemmas": ga["lemmas"], "definition": ga["definition"], "example": ga["example"],
        })

    # Two items matched to the same synset are merged: lemmas unioned, the
    # first definition and example kept.
    merged = {}
    for item in matched:
        if item["ili"] in merged:
            prev = merged[item["ili"]]
            print(f"Horizon: merging duplicate items for {item['synset_id']}: "
                  f"{prev['en_lemmas']} / {item['en_lemmas']}")
            known = {key(l) for l in prev["lemmas"]}
            prev["lemmas"] += [l for l in item["lemmas"] if key(l) not in known]
            prev["definition"] = prev["definition"] or item["definition"]
            prev["example"] = prev["example"] or item["example"]
        else:
            merged[item["ili"]] = item
    with open(BUILD / "horizon.json", "w", encoding="utf-8") as f:
        json.dump(list(merged.values()), f, ensure_ascii=False, indent=1)
    methods = defaultdict(int)
    for item in matched:
        methods[item["match"]] += 1
    print(f"Horizon: {len(matched)} matched ({dict(methods)}), "
          f"{len(merged)} synsets, {len(unmatched)} unmatched")
    write_tsv(BUILD / "horizon_unmatched.tsv",
              ["en_lemmas", "en_definition", "en_example", "ga_lemmas", "best_guess"], unmatched)


if __name__ == "__main__":
    main()
