<p align="center"><img src="logo.svg" alt="GréasánFocal" width="160"></p>

# GréasánFocal Oscailte na Gaeilge

*Open Irish Wordnet* · [Gaeilge](#gaeilge) · [English](#english)

---

## Gaeilge

Is gréasán focal (*wordnet*) don Ghaeilge é **GréasánFocal Oscailte na Gaeilge**. Is bunachar sonraí foclóireachta é a ghrúpálann focail Ghaeilge i synsets ("tacair chomhchiallaigh"). Nascann sé na tacair sin le gaolta séimeantacha, mar shampla an gaol idir *madra* agus *ainmhí*. Tá gach tacar ailínithe leis an [Open English Wordnet](https://en-word.net/) (OEWN) tríd an Collaborative Interlingual Index (ILI). Mar sin, is féidir an acmhainn a úsáid in éineacht le OEWN agus le líonraí focal i dteangacha eile.

Tá thart ar 8,000 coincheapa agus 11,000 ciall san eagrán reatha. Níl sainmhíniú Gaeilge ag go leor tacar fós. Ina áit sin, taispeántar sainmhíniú Béarla OEWN, marcáilte le scór muiníne 0.0. Is bealach iontach chun cabhrú iad a aistriú go Gaeilge.

### Eagarthóireacht

Tá an líonra stóráilte mar chomhaid YAML in [`src/yaml/`](src/yaml/). Cuirtear in eagar iad le **[EWE](https://github.com/jmccrae/ewe)** (EWE Wordnet Editor). Ná cuir na comhaid in eagar de láimh. Coinníonn EWE na hiontrálacha, na cialla agus na gaolta comhsheasmhach, agus bailíochtaíonn sé gach athrú.

```bash
git clone https://github.com/jmccrae/ewe && cd ewe
cargo build --release              # cruthaíonn sé seo target/release/ewe-cli
```

- **Líne na n-orduithe:** rith `ewe-cli --wordnet .` san fhillteán seo chun roghchlár eagarthóireachta a oscailt. Is féidir baisc athruithe a scríobh mar chomhad YAML freisin agus é a rith le `ewe-cli automaton athruithe.yaml --wordnet .`.
- **Eagarthóir gréasáin nó deisce:** léann eagarthóir grafach EWE an comhad [`settings.toml`](settings.toml) san fhillteán seo (lógó, dathanna, srl.). Féach [cáipéisíocht EWE](https://github.com/jmccrae/ewe/tree/main/ewe_dioxus).
- **Easpórtáil:** cruthaíonn `make xml` comhad WN-LMF XML in `build/gfong.xml`.

### Cur leis an tionscadal

Fáiltítear roimh gach cabhair: ceartúcháin, focail nua, sainmhínithe agus samplaí Gaeilge.

1. Déan forc den stór seo agus cuir na hathruithe in eagar le EWE.
2. Bí cinnte go n-éiríonn le bailíochtú EWE (ní shábhálann EWE athruithe neamhbhailí).
3. Oscail iarratas tarraingthe (*pull request*), ceann amháin do gach ábhar. Nó oscail ceist (*issue*) má aimsíonn tú botún nach féidir leat a cheartú tú féin.

**Nuair a scríobhann tú sainmhíniú Gaeilge in áit sainmhínithe Béarla**, bain an scór muiníne 0.0 freisin. Fanann an scór nuair a athraítear téacs an tsainmhínithe:

```yaml
- change_definition: {synset: 01316879-n, definition: "ainmhí nó feithid a dhéanann damáiste do bharra nó do bheostoc"}
- set_confidence: {synset: 01316879-n, definition: 1}   # gan scór = muinín iomlán
```

### Ceadúnas

[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Tá an acmhainn bunaithe go páirteach ar [Líonra Séimeantach na Gaeilge](http://borel.slu.edu/lsg/) (Kevin P. Scannell), ar an [Open English Wordnet](https://github.com/globalwordnet/english-wordnet) agus ar [Wikidata](https://www.wikidata.org/).

---

## English

**GréasánFocal Oscailte na Gaeilge** (*Open Irish Wordnet*) is a wordnet for Irish. It is a lexical database that groups Irish words into sets of synonyms (*synsets*) and links them by semantic relations, such as the one between *madra* (dog) and *ainmhí* (animal). Every synset is aligned to the [Open English Wordnet](https://en-word.net/) (OEWN) through the Collaborative Interlingual Index (ILI). This means the resource can be used alongside OEWN and wordnets in other languages.

The current release has about 8,000 synsets and 11,000 senses. Many synsets don't have an Irish definition yet. These show the English OEWN definition instead, marked with a confidence score of 0.0, and translating them into Irish is a great way to help.

### Editing

The wordnet is stored as YAML files in [`src/yaml/`](src/yaml/). Edit them with **[EWE](https://github.com/jmccrae/ewe)** (EWE Wordnet Editor), not by hand. EWE keeps entries, senses and relations consistent and validates every change.

```bash
git clone https://github.com/jmccrae/ewe && cd ewe
cargo build --release              # builds target/release/ewe-cli
```

- **Command line:** run `ewe-cli --wordnet .` in this folder to open an editing menu. You can also script a batch of changes as a YAML file and run it with `ewe-cli automaton changes.yaml --wordnet .`.
- **Web or desktop editor:** EWE's graphical editor reads this folder's [`settings.toml`](settings.toml) (logo, colours, etc.). See the [EWE documentation](https://github.com/jmccrae/ewe/tree/main/ewe_dioxus).
- **Export:** `make xml` writes a WN-LMF XML file to `build/gfong.xml`.

### Contributing

All help is welcome: corrections, new words, and Irish definitions and examples.

1. Fork this repository and make your changes with EWE.
2. Make sure EWE's validation passes. EWE won't save invalid changes.
3. Open a pull request, one per topic. Or open an issue if you find a mistake you can't fix yourself.

**When you replace an English definition with an Irish one**, also remove its 0.0 confidence score. The score is kept when a definition's text is changed:

```yaml
- change_definition: {synset: 01316879-n, definition: "ainmhí nó feithid a dhéanann damáiste do bharra nó do bheostoc"}
- set_confidence: {synset: 01316879-n, definition: 1}   # no score = full confidence
```

### Licence

[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Based in part on [Líonra Séimeantach na Gaeilge](http://borel.slu.edu/lsg/) (Kevin P. Scannell), the [Open English Wordnet](https://github.com/globalwordnet/english-wordnet) and [Wikidata](https://www.wikidata.org/).
