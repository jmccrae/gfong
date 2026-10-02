---
name: wordnet-editing
description: Use when editing GréasánFocal Oscailte na Gaeilge, the Irish wordnet in this repository (adding/deleting synsets, entries, relations, examples, or changing ILI/Wikidata links), through the ewe_mcp MCP server's tools or ewe-cli automaton scripts. Covers aligning synsets with the Open English Wordnet, Irish lemma forms, Irish genus/differentia definitions, the English placeholder definitions, provenance in `source`, lexfile selection, hypernyms, sense vs. synset relations, safe entry moves, and when synset deletion/merging is appropriate - not the tool call syntax itself, which the tools' own schemas already cover.
---

# Editing GréasánFocal with EWE

GréasánFocal Oscailte na Gaeilge is an Irish wordnet aligned to the Open English
Wordnet (OEWN): every synset is an OEWN synset with Irish lemmas, sharing its synset
id and ILI.

This skill assumes an `ewe_mcp` MCP server is connected, exposing `lookup_word`,
`lookup_id`, `search_prefix`, `validate`, `apply_automaton`, and `save`. Their
parameters and return shapes are already fully described by the tools' own JSON
schemas - don't re-derive or guess at them here. Without the MCP server, write the
same actions as a YAML automaton file and run
`echo n | ewe-cli automaton changes.yaml --wordnet .` (the `echo n` declines EWE's
"save anyway?" prompt if validation fails). What this skill covers is the *judgment*
a schema can't express: which synset, which lemma form, which relation, when deletion
is actually the right call.

## Structure of the wordnet

- A synset id is 8 digits plus a part-of-speech suffix (e.g. `00001740-n`), and is
  the id of the corresponding OEWN synset. **Never invent one.** To add an Irish
  word for a concept not yet in GréasánFocal, find the OEWN synset for it and pass
  its id and ILI to `add_synset` as `id` and `ili` (see "Adding a new synset").
- Concepts with no OEWN equivalent (Irish-specific senses) can't be added yet: a
  synset without an ILI can't be exported to WN-LMF XML for a non-English wordnet
  (ewe#33). Raise these as an issue instead.
- Every noun synset needs at least one hypernym link, and every verb synset should
  have one wherever OEWN has one. A noun with none will fail `validate`.

## Lemmas

Use the Irish dictionary form, as in [foclóir.ie](https://www.focloir.ie/) or
[teanglann.ie](https://www.teanglann.ie/):

- nouns in the nominative singular (*bó*, not *ba* or *bhó*);
- verbs as the second person singular imperative (*caill*, *dear*), not the verbal
  noun (*cailleadh*) unless the synset is a noun;
- adjectives in the masculine nominative singular (*mór*);
- no initial mutation on the first word, but keep the mutations a multi-word
  expression takes inside it (*áit pháirceála*, *bí ag súil le*).

Order a synset's lemmas from most to least usual; the first is shown as the synset's
headword. `change_members` sets the full, ordered list in one action, adding and
removing entries as needed.

## Definitions

Definitions are written in Irish: short (3-15 words), phrased as a genus and a
differentia. E.g. *láir* is a *capall* (genus), differentiated by *baineann*
(differentia): "capall baineann".

Many synsets don't have an Irish definition yet. They carry the English OEWN
definition as a placeholder, marked with a definition confidence of 0.0. When you
write the Irish definition, replace the English one with `change_definition` and
then clear the score with `set_confidence` (synset, `definition: 1`, no
`confidence`): rewording a definition keeps its existing score, so without this the
new Irish definition would still be marked as a 0.0 placeholder.

## Provenance (`source`)

Each synset's `source` records where its lemmas came from, grouped by source, e.g.
`'LSG, Wisteria: foirceann; review: foirceannadh'`. LSG, Wikidata, Wisteria and
Horizon are the sources of the initial build, and `review` marks lemmas added or
corrected by hand. EWE doesn't update it: when you add or replace a lemma, update it
with `change_source`, listing the new lemma under `review` (and drop removed lemmas).

## Adding a new synset

1. Find the OEWN synset for the concept, and note its id, ILI, lexfile and hypernyms
   (e.g. on [en-word.net](https://en-word.net/) or in an english-wordnet checkout).
2. Settle on the Irish lemmas and an Irish definition.
3. Find a hypernym target: OEWN's hypernym if it is already in GréasánFocal (check
   with `lookup_id`), otherwise its nearest OEWN ancestor that is.
4. Use the OEWN synset's lexfile - see `references/lexfiles.md`.
5. One `apply_automaton` call: an `add_synset` action (`id`, `ili`, definition,
   lexfile, pos, lemmas), an `add_relation` with `relation: "hypernym"`,
   `source: "last"` and `target: <the id from step 3>`, and a `change_source`
   recording the lemmas as `review`.
6. Always `dry_run: true` first for anything beyond a single trivial action - see
   "Check before you commit" below.

## Updating relations

Relations are either between two **synsets** (just `source`/`target`) or two **senses**
(also give `source_sense`/`target_sense`, as a sense id or - more convenient when you
already know the lemma - `source_lemma`/`target_lemma`). Get a sense id via
`lookup_word(word, sense_ids: true)`.

Follow OEWN's relations where both synsets are in GréasánFocal. The full relation name
lists (which apply to synsets vs. senses) are in `references/relations.md` rather than
repeated here. Most have an inverse the tool maintains automatically
(`hypernym`/`hyponym`, `holo_*`/`mero_*`, etc.) - add whichever direction reads
naturally, not both.

### Entries

To relocate a lemma from one synset to another, use `move_entry` rather than a
`delete_entry` + `add_entry` pair - it carries the entry's existing sense relations,
forms, and pronunciations across instead of dropping them. Use plain `add_entry`/
`delete_entry` when there's nothing to carry over.

A lemma that is a wrong translation for a synset (the right word for a different
sense) should be moved to the synset it does translate if that synset is in
GréasánFocal, and otherwise deleted.

## Deleting synsets

Only appropriate in a few specific cases: merging/deduplicating two synsets that
describe the same sense, correcting a synset introduced by an error, or - only if
explicitly asked - a concept that has no Irish lexicalisation at all. It is not a
general cleanup tool.

- `reason` should name the issue driving the deletion, e.g. `"Duplicate (#123)"`. This
  convention isn't enforced by `apply_automaton` itself (unlike `ewe_cli`'s interactive
  menu, which rejects a reason without a `(#N)` suffix) - hold yourself to it anyway,
  since it's the only record of *why* a synset disappeared.
- Prefer giving `superseded_by`: it hands off the deleted synset's entries, relations,
  and examples to the target and leaves a deprecation record. Omit it only for a
  no-trail permanent removal - appropriate for e.g. a synset you created earlier in the
  *same* session and decided against, not for anything that might already be referenced
  elsewhere.

## Other edits

`change_definition`, `add_example`/`update_example`/`delete_example`, `change_ili`, and
`change_wikidata` actions cover the rest - their parameters are in the tool schema, not
repeated here. Conventions worth knowing:

- Examples are Irish sentences using the lemma, written naturally rather than
  translated word for word from OEWN's English example.
- Use Unicode curly quotes (‘ ’) and apostrophes (’) in examples, not straight ones.
- An example's `source` is optional - omit it rather than inventing one.
- Don't change a synset's ILI: it is what aligns the synset with OEWN.

## Confidence scores

A confidence score records how sure the wordnet is of a synset, sense, entry, definition,
example or relation (WN-LMF `confidenceScore`, 0.0-1.0; no score means 1.0). Set one only
when you have an actual reason to doubt the item - e.g. an automatically generated or
unverified addition - not as routine annotation of your own edits.

- When creating something, give the score inline: `confidence` on `add_synset`, `add_entry`,
  `add_example` and `add_relation`; `definition_confidence` on `add_synset`; `entry_confidence`
  on `add_entry`.
- To re-score something that already exists, use `set_confidence`.
- Rewording a definition or example keeps its existing score. If your edit resolves the doubt,
  clear the score by sending `set_confidence` without `confidence`.

## Check before you commit

For anything beyond a single trivial action, call `apply_automaton` with
`dry_run: true` first. It runs the exact same apply against an in-memory copy and
reports `would_succeed` plus any `validation_errors` the change would introduce,
without touching the real wordnet. Fix and re-check if needed, then call again with
`dry_run` omitted (or `false`) to actually apply.

A real apply already validates and auto-saves when the result is clean. If it comes
back with `saved: false` and validation errors, fix the underlying issue and reapply -
don't reach for `save(force: true)`. That's a deliberate, rare override for a change
you've decided to keep despite an existing validation error, not a routine step.

Never edit the YAML in `src/yaml/` by hand: CI validates every push with EWE and
fails if the files differ from what EWE would write.
