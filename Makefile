# Build GréasánFocal Oscailte na Gaeilge from its sources.
#
#   make          extract the sources, vote and write build/automaton.yaml
#   make wordnet  empty src/yaml/ and rebuild it with EWE (discards manual edits!)
#   make xml      export build/gfong.xml
#
# Requires an EWE with confidence scores and add_synset id/ili
# (jmccrae/ewe#63, #64).

EWE ?= $(HOME)/projects/jmccrae/ewe/target/release/ewe-cli
PYTHON ?= python3
VERSION ?= 0.1

B := build
S := scripts

all: $(B)/automaton.yaml

$(B)/oewn.tsv $(B)/oewn_rels.tsv: $(S)/oewn.py
	$(PYTHON) $<
$(B)/lsg.tsv $(B)/lsg_defs.tsv: $(S)/lsg.py lsg-lmf.xml
	$(PYTHON) $<
$(B)/wisteria.tsv: $(S)/wisteria.py $(B)/oewn.tsv
	$(PYTHON) $<
$(B)/wikidata.tsv: $(S)/wikidata.py $(B)/oewn.tsv
	$(PYTHON) $<
$(B)/horizon.json: $(S)/horizon.py $(B)/oewn.tsv horizon_translations/*.txt
	$(PYTHON) $<
$(B)/synsets.json: $(S)/vote.py $(B)/lsg.tsv $(B)/wisteria.tsv $(B)/wikidata.tsv $(B)/horizon.json
	$(PYTHON) $<
$(B)/relations.tsv: $(S)/hypernyms.py $(B)/synsets.json $(B)/oewn_rels.tsv
	$(PYTHON) $<
$(B)/automaton.yaml: $(S)/make_automaton.py $(B)/synsets.json $(B)/relations.tsv
	$(PYTHON) $<

wordnet: $(B)/automaton.yaml
	for f in src/yaml/*.yaml; do : > $$f; done
	printf '"ID","ILI","SUPERSEDED_BY","SUPERSEDING_ILI","REASON"\n' > src/deprecations.csv
	$(EWE) automaton $< --wordnet .

xml:
	$(EWE) export xml $(B)/gfong.xml --wordnet . --id-prefix gfong \
	  --label "GréasánFocal Oscailte na Gaeilge" --language ga \
	  --license https://creativecommons.org/licenses/by-sa/4.0/ --version $(VERSION) \
	  --email john@mccr.ae --url https://irishwn.teanga.io/

clean:
	rm -rf $(B)

.PHONY: all wordnet xml clean
