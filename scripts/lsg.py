"""Extract lemmas and Irish definitions from the LSG wordnet (lsg-lmf.xml).

Synsets are mapped through their `ili` attribute; synsets with no ILI (the
195 LSG-specific `lsg-50xxxxxx` synsets) are dropped.

Writes:
  build/lsg.tsv        ili, lemma
  build/lsg_defs.tsv   ili, definition
"""
from lxml import etree

from common import BUILD, LSG_XML, norm, write_tsv


def main():
    senses = []  # (lemma, synset id)
    synset_ili, definitions = {}, []
    lemma = None
    for _, el in etree.iterparse(str(LSG_XML), events=("end",), load_dtd=False,
                                 no_network=True, resolve_entities=False):
        if el.tag == "Lemma":
            lemma = norm(el.get("writtenForm"))
        elif el.tag == "Sense":
            senses.append((lemma, el.get("synset")))
        elif el.tag == "Synset":
            ili = el.get("ili", "")
            if ili and ili != "in":
                synset_ili[el.get("id")] = ili
                for d in el.findall("Definition"):
                    if d.text and d.text.strip():
                        definitions.append((ili, norm(d.text)))
            el.clear()
        elif el.tag == "LexicalEntry":
            el.clear()
    dropped = sum(1 for _, ss in senses if ss not in synset_ili)
    print(f"LSG: {len(senses)} senses, {dropped} dropped (no ILI)")
    write_tsv(BUILD / "lsg.tsv", ["ili", "lemma"],
              sorted({(synset_ili[ss], l) for l, ss in senses if ss in synset_ili}))
    write_tsv(BUILD / "lsg_defs.tsv", ["ili", "definition"], definitions)


if __name__ == "__main__":
    main()
