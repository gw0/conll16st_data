conll16st_data
==============

Although the data format for the [*CoNLL 2016 Shared Task*](http://www.cs.brandeis.edu/~clp/conll16st/) (Multilingual Shallow Discourse Parsing) seems useful from the human perspective, it is very specific and needs a lot of preprocessing to be used in machine learning context. To make your life easier, we developed this **data preprocessor** with the goal to access *CoNLL16st*/*CoNLL15st* datasets from *Python* in an even **simpler and task-agnostic representation**.

- <http://www.cs.brandeis.edu/~clp/conll16st/>
- <http://github.com/attapol/conll16st/>
- <http://github.com/gw0/conll16st_data/>


Installation
============

Install requirements, get source code, and locate your dataset (eg. `./conll16st_data/conll16st-en-trial/`):

```bash
$ pip install pyparsing
$ git clone http://github.com/gw0/conll16st_data/
$ ls -1 ./conll16st_data/conll16st-en-trial/
parses.json
raw/
relations.json
relations-no-senses.json
```


Basic usage
===========

Load whole **dataset as object** and iterate over first words and POS tags:

```python
from conll16st_data.load import Conll16stDataset

print("load dataset for training")
train = Conll16stDataset("./conll16st_data/conll16st-en-trial/")
print(train.summary())

for doc_id in train['doc_ids']:
    first_word = train['words'][doc_id][0]
    first_pos_tag = train['pos_tags'][doc_id][0]

    print("{}: first word is '{}' with POS tag '{}'".format(doc_id, first_word, first_pos_tag))
```

```bash
$ python example.py
load dataset for training
  ./conll16st_data/conll16st-en-trial/: doc_ids: 1, words: 896, rel_ids: 29, relation tokens: 1064
wsj_1000: first word is 'Kemper' with POS tag 'NNP'
```

In the above object all aspects of the dataset are accessible like a dictionary:

- `train['doc_ids']` - list of document ids
- `train['words']` - words by [document id, token id]
- `train['word_metas']` - word meta data by [document id, token id]
- `train['pos_tags']` - POS tags by [document id, token id]
- `train['dependencies']` - dependencies by [document id, token_1 id, token_2 id]
- `train['parsetrees']` - parse tree with POS tags by [document id]
- `train['rel_ids']` - list of relation ids
- `train['rel_parts']` - argument 1, argument 2, connective, punctuation, and meta data of relations by [relation id]
- `train['rel_types']` - relation types by [relation id]
- `train['rel_senses']` - relation senses by [relation id]

Alternatively load **dataset into Python dictionaries** and filter by document ids, discourse types and senses:

```python
from conll16st_data.load import load_all

dataset_dir = "./conll16st_data/conll16st-en-trial/"
doc_ids = ["wsj_1000"]
filter_types = ["Explicit"]
filter_senses = ["Contingency.Condition"]

doc_ids, words, word_metas, pos_tags, dependencies, parsetrees, \
rel_ids, rel_parts, rel_types, rel_senses, relations_gold = \
  load_all(dataset_dir, doc_ids=doc_ids, filter_types=filter_types, filter_senses=filter_senses)
```


Advanced usage
==============

Load provided *CoNLL16st*/*CoNLL15st* files untouched (as in tutorial):

```python
from conll16st_data.files import load_parses, load_raws, load_relations_gold

dataset_dir = "./conll16st_data/conll16st-en-trial/"
doc_ids = ["wsj_1000"]
filter_types = ["Explicit"]
filter_senses = ["Contingency.Condition"]

parses = load_parses(dataset_dir, doc_ids=doc_ids)
doc_ids = sorted(parses.keys())
raws = load_raws(dataset_dir, doc_ids=doc_ids)
relations_gold = load_relations_gold(dataset_dir, doc_ids=doc_ids, with_senses=True, filter_types=filter_types, filter_senses=filter_senses)
```

```python
# examples of data:
parses["wsj_1000"]['sentences'][0]['words'][0] = [
    'Kemper',
    {'CharacterOffsetEnd': 15, 'Linkers': ['arg1_14890'], 'PartOfSpeech': 'NNP', 'CharacterOffsetBegin': 9}
]
raws["wsj_1000"] = ".START \n\nKemper Financial Services Inc., charging..."
relations[14905] = {
    'Arg1': {'CharacterSpanList': [[4564, 4610]], 'RawText': 'this prompts ...', 'TokenList': [[4564, 4568, 879, 32, 2], [4569, 4576, 880, 32, 3], ...]},
    'Arg2': {'CharacterSpanList': [[4557, 4560], [4617, 4650]], 'RawText': 'But it ...', 'TokenList': [[4557, 4560, 877, 32, 0], [4617, 4619, 889, 32, 12], ...]},
    'Connective': {'CharacterSpanList': [[4561, 4563], [4612, 4616]], 'RawText': 'if then', 'TokenList': [[4561, 4563, 878, 32, 1], [4612, 4616, 888, 32, 11]]},
    'Punctuation': {'CharacterSpanList': [], 'RawText': '', 'TokenList': [], 'PunctuationType': ''},
    'DocID': 'wsj_1000',
    'ID': 14905,
    'Sense': ['Contingency.Condition'],
    'Type': 'Explicit',
}
```

Extract data by document id and token id (`words`, `pos_tags`, `word_metas`):

```python
from conll16st_data.words import get_words, get_pos_tags, get_word_metas

words = get_words(parses)
pos_tags = get_pos_tags(parses)
word_metas = get_word_metas(parses, raws)
```

```python
# examples of data:
words["wsj_1000"] = ["Kemper", "Financial", "Services", "Inc.", ",", "charging", ...]
pos_tags["wsj_1000"] = ["NNP", "NNP", "NNPS", "NNP", ",", "VBG", ...]
word_metas['wsj_1000'][0] = {
    'Text': 'Kemper',
    'DocID': 'wsj_1000',
    'ParagraphID': 0,
    'SentenceID': 0,
    'SentenceOffset': 0,
    'TokenID': 0,
    'RelationIDs': [14890],
    'RelationParts': ['Arg1'],
}
```

Extract data by document id and token id pairs (`dependencies`):

```python
from conll16st_data.dependencies import get_dependencies

dependencies = get_dependencies(parses)
```

```python
# example ["nn", "Inc.-4", "Kemper-1"] becomes:
dependencies["wsj_1000"][3][0] = "nn"
```

Extract data by document id (`parsetrees`):

```python
from conll16st_data.parsetrees import get_parsetrees

parsetrees = get_parsetrees(parses)
```

```python
# example "( (S (NP (NNP Kemper) (NNP Financial) (NNPS Services)..." becomes:
parsetrees["wsj_1000"][0] = [[u'S', [u'NP', [u'NNP', 0], [u'NNP', 1], [u'NNPS', 2], ...
```

Extract data by relation id (`rel_parts`, `rel_ids`, `rel_types`, `rel_senses`):

```python
from conll16st_data.relations import get_rel_parts, get_rel_types, get_rel_senses

rel_parts = get_rel_parts(relationsnos_gold)
rel_ids = sorted(rel_parts.keys())
rel_types = get_rel_types(relations_gold)
rel_senses = get_rel_senses(relations_gold)
```

```python
# examples of data:
rel_parts[14905] = {
    'Arg1': [879, 880, 881, 882, 883, 884, 885, 886],
    'Arg1Len': 46,
    'Arg2': [877, 889, 890, 891, 892, 893, 894],
    'Arg2Len': 36,
    'Connective': [878, 888],
    'ConnectiveLen': 6,
    'Punctuation': [],
    'PunctuationLen': 0,
    'PunctuationType': '',
    'DocID': 'wsj_1000',
    'ID': 14905,
    'TokenMin': 877,
    'TokenMax': 894,
    'TokenCount': 17,
}
rel_types[14905] = "Explicit"
rel_senses[14905] = "Contingency.Condition"
```

Add extra fields (relation tags to word_metas):

```python
from conll16st_data.relations import add_relation_tags

add_relation_tags(word_metas, rel_types, rel_senses)
```

```python
# examples of data:
word_metas['wsj_1000'][0] = {
    ...
    'RelationTags': ["Explicit:Expansion.Conjunction:14890:Arg1"],
}
```


Development
===========

Install requirements (with *virtualenv*) and get source code:

```bash
$ virtualenv venv
$ . venv/bin/activate
$ pip install pyparsing pytest
$ git clone http://github.com/gw0/conll16st_data/
```

Also remember to test code (with *pytest*) before commiting:

```bash
$ cd ./conll16st_data
$ py.test *.py
========================= test session starts =========================
platform linux2 -- Python 2.7.9, pytest-2.9.1, py-1.4.31, pluggy-0.3.1
rootdir: .../conll16st_data, inifile: 
collected 13 items 

dependencies.py .
files.py ....
parsetrees.py .
relations.py ....
words.py ...

====================== 13 passed in 0.56 seconds ======================
```


Feedback
========

If you encounter any bugs or have feature requests, please file them in the [issue tracker](http://github.com/gw0/conll16st_data/issues/), or even develop it yourself and submit a pull request on [GitHub](http://github.com/gw0/conll16st_data/).


License
=======

Copyright &copy; 2016 *gw0* [<http://gw.tnode.com/>] &lt;<gw.2016@tnode.com>&gt;

This code is licensed under the [GNU Affero General Public License 3.0+](LICENSE_AGPL-3.0.txt) (*AGPL-3.0+*). Note that it is mandatory to make all modifications and complete source code publicly available to any user.
