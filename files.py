#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0103
"""
Load provided CoNLL16st/CoNLL15st files untouched.
"""
__author__ = "GW [http://gw.tnode.com/] <gw.2016@tnode.com>"
__license__ = "GPLv3+"

import codecs
import json


def load_parses(dataset_dir, doc_ids=None, parses_ffmts=None):
    """Load parses and tags untouched from CoNLL16st corpus.

        parses["wsj_1000"]['sentences'][0]['words'][0] = [
            'Kemper',
            {'CharacterOffsetEnd': 15, 'Linkers': ['arg1_14890'], 'PartOfSpeech': 'NNP', 'CharacterOffsetBegin': 9}
        ]
    """
    if parses_ffmts is None:
        parses_ffmts = [
            "{}/parses.json",             # CoNLL16st filenames
            "{}/pdtb-parses.json",        # CoNLL15st filenames
            "{}/pdtb_trial_parses.json",  # CoNLL15st trial filenames
        ]

    # load all parses
    parses = {}
    for parses_ffmt in parses_ffmts:
        try:
            f = codecs.open(parses_ffmt.format(dataset_dir), 'r', encoding='utf8')
            parses = json.load(f)
            f.close()
            break
        except IOError:
            pass

    # filter by document id
    if doc_ids is not None:
        parses = { doc_id: parses[doc_id]  for doc_id in doc_ids }
    return parses


def load_raws(dataset_dir, doc_ids, raw_ffmts=None):
    """Load raw text untouched by document id from CoNLL16st corpus.

        raws["wsj_1000"] = ".START \n\nKemper Financial Services Inc., charging..."
    """
    if raw_ffmts is None:
        raw_ffmts = [
            "{}/raw/{}",  # CoNLL16st/CoNLL15st filenames
        ]

    # load all raw texts
    raws = {}
    for doc_id in doc_ids:
        raws[doc_id] = None
        for raw_ffmt in raw_ffmts:
            try:
                # open using utf8 encoding
                f = codecs.open(raw_ffmt.format(dataset_dir, doc_id), 'r', encoding='utf8')
                try:
                    raws[doc_id] = f.read()
                except UnicodeDecodeError:
                    f.close()
                    # fallback to binary reading
                    f = open(raw_ffmt.format(dataset_dir, doc_id), 'r')
                    raws[doc_id] = f.read()
                f.close()
                break  # skip other filenames
            except IOError:
                pass
        if not raws[doc_id]:
            raise IOError("Failed to load raw text ({})!".format(doc_id))
    return raws


def load_relations_gold(dataset_dir, with_senses=True, with_rawtext=False, doc_ids=None, filter_types=None, filter_senses=None, filter_fn=None, relations_ffmts=None):
    """Load shallow discourse relations untouched by relation id from CoNLL16st corpus.

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
    """
    if relations_ffmts is None:
        relations_ffmts = []
        relations_ffmts += [
            "{}/relations.json",        # CoNLL16st filenames
            "{}/pdtb-data.json",        # CoNLL15st filenames
            "{}/pdtb_trial_data.json",  # CoNLL15st trial filenames
        ]
        if not with_senses:
            relations_ffmts += [
                "{}/relations-no-senses.json",  # CoNLL16st filenames
            ]

    # load all relations
    relations = {}
    for relations_ffmt in relations_ffmts:
        try:
            f = codecs.open(relations_ffmt.format(dataset_dir), 'r', encoding='utf8')
            for line in f:
                relation = json.loads(line)

                # filter by document id
                if doc_ids and relation['DocID'] not in doc_ids:
                    continue

                # filter by relation type
                if filter_types and relation['Type'] and relation['Type'] not in filter_types:
                    continue

                # filter by relation senses
                if filter_senses and relation['Sense']:
                    relation['Sense'] = list(set(relation['Sense']).intersection(set(filter_senses)))
                    if not relation['Sense']:
                        continue

                # fix inconsistent structure
                if 'TokenList' not in relation['Arg1']:
                    relation['Arg1']['TokenList'] = []
                if 'TokenList' not in relation['Arg2']:
                    relation['Arg2']['TokenList'] = []
                if 'TokenList' not in relation['Connective']:
                    relation['Connective']['TokenList'] = []
                if 'Punctuation' not in relation:
                    relation['Punctuation'] = {'CharacterSpanList': [], 'PunctuationType': "", 'RawText': "", 'TokenList': []}
                if 'PunctuationType' not in relation['Punctuation']:
                    relation['Punctuation']['PunctuationType'] = ""
                if 'TokenList' not in relation['Punctuation']:
                    relation['Punctuation']['TokenList'] = []

                # filter by lambda expression on relation
                if filter_fn and filter_fn(relation):
                    continue

                # remove type and sense information
                if not with_senses:
                    relation['Sense'] = []
                    relation['Type'] = ""

                # remove raw text fields
                if not with_rawtext:
                    relation['Arg1']['RawText'] = None
                    relation['Arg2']['RawText'] = None
                    relation['Connective']['RawText'] = None
                    relation['Punctuation']['RawText'] = None

                # save relation
                relations[relation['ID']] = relation
            f.close()
            break
        except IOError:
            pass
    return relations


def strip_relations_gold(relations):
    """Strip type and sense information from shallow discourse relations from CoNLL16st corpus."""

    relationsnos = {}
    for rel_id, relation in relations.iteritems():
        relation = dict(relation)  # copy dict

        # remove type and sense information
        relation['Sense'] = []
        relation['Type'] = ""

        # save relation
        relationsnos[rel_id] = relation
    return relationsnos


### Tests

def test_parses():
    dataset_dir = "./conll16st-en-trial"
    t_doc_id = "wsj_1000"
    t_s0_word0 = "Kemper"
    t_s0_word0_linkers = ["arg1_14890"]
    t_s0_word0_pos = "NNP"
    t_s0_parsetree = "( (S (NP (NNP Kemper) (NNP Financial) (NNPS Services)"
    t_s0_dependency0 = ["root", "ROOT-0", "cut-16"]
    t_s0_dependency1 = ["nn", "Inc.-4", "Kemper-1"]

    parses = load_parses(dataset_dir)
    s0 = parses[t_doc_id]['sentences'][0]
    assert s0['words'][0][0] == t_s0_word0
    assert s0['words'][0][1]['Linkers'] == t_s0_word0_linkers
    assert s0['words'][0][1]['PartOfSpeech'] == t_s0_word0_pos
    assert s0['parsetree'].startswith(t_s0_parsetree)
    assert t_s0_dependency0 in s0['dependencies']
    assert t_s0_dependency1 in s0['dependencies']

def test_raws():
    dataset_dir = "./conll16st-en-trial"
    doc_id = "wsj_1000"
    t_raw = ".START \n\nKemper Financial Services Inc., charging"

    raws = load_raws(dataset_dir, [doc_id])
    assert raws[doc_id].startswith(t_raw)

def test_relations():
    dataset_dir = "./conll16st-en-trial"
    t_rel0 = {
        'Arg1': {'CharacterSpanList': [[4564, 4610]], 'RawText': 'this prompts others to consider the same thing', 'TokenList': [[4564, 4568, 879, 32, 2], [4569, 4576, 880, 32, 3], [4577, 4583, 881, 32, 4], [4584, 4586, 882, 32, 5], [4587, 4595, 883, 32, 6], [4596, 4599, 884, 32, 7], [4600, 4604, 885, 32, 8], [4605, 4610, 886, 32, 9]]},
        'Arg2': {'CharacterSpanList': [[4557, 4560], [4617, 4650]], 'RawText': 'But it may become much more important', 'TokenList': [[4557, 4560, 877, 32, 0], [4617, 4619, 889, 32, 12], [4620, 4623, 890, 32, 13], [4624, 4630, 891, 32, 14], [4631, 4635, 892, 32, 15], [4636, 4640, 893, 32, 16], [4641, 4650, 894, 32, 17]]},
        'Connective': {'CharacterSpanList': [[4561, 4563], [4612, 4616]], 'RawText': 'if then', 'TokenList': [[4561, 4563, 878, 32, 1], [4612, 4616, 888, 32, 11]]},
        'Punctuation': {'CharacterSpanList': [], 'RawText': '', 'TokenList': [], 'PunctuationType': ''},
        'DocID': 'wsj_1000',
        'ID': 14905,
        'Sense': ['Contingency.Condition'],
        'Type': 'Explicit',
    }
    t_rel1 = dict(t_rel0)
    t_rel1['Sense'] = []
    t_rel1['Type'] = ""

    relations = load_relations_gold(dataset_dir, with_senses=True, with_rawtext=True)
    rel0 = relations[t_rel0['ID']]
    for span in ['Arg1', 'Arg2', 'Connective', 'Punctuation']:
        for k in ['CharacterSpanList', 'RawText', 'TokenList']:
            assert rel0[span][k] == t_rel0[span][k], (span, k)
    assert rel0['Punctuation']['PunctuationType'] == t_rel0['Punctuation']['PunctuationType']
    assert rel0 == t_rel0

    relationsnos = strip_relations_gold(relations)
    rel1 = relationsnos[t_rel1['ID']]
    for span in ['Arg1', 'Arg2', 'Connective', 'Punctuation']:
        for k in ['CharacterSpanList', 'RawText', 'TokenList']:
            assert rel1[span][k] == t_rel1[span][k], (span, k)
    assert rel1['Punctuation']['PunctuationType'] == t_rel1['Punctuation']['PunctuationType']
    assert rel1 == t_rel1

def test_relations_filtered():
    dataset_dir = "./conll16st-en-trial"
    doc_id = "wsj_1000"
    filter_types = ["Implicit"]
    filter_senses = ["Comparison.Contrast"]
    t_rel0_fail_id = 14905  # is Explicit:Contingency.Condition
    t_rel1 = {
        'Arg1': {'CharacterSpanList': [[2447, 2552]], 'RawText': None, 'TokenList': [[2447, 2449, 457, 15, 0], [2449, 2452, 458, 15, 1], [2453, 2459, 459, 15, 2], [2460, 2462, 460, 15, 3], [2463, 2473, 461, 15, 4], [2474, 2476, 462, 15, 5], [2477, 2482, 463, 15, 6], [2483, 2492, 464, 15, 7], [2493, 2496, 465, 15, 8], [2497, 2501, 466, 15, 9], [2502, 2506, 467, 15, 10], [2507, 2509, 468, 15, 11], [2510, 2514, 469, 15, 12], [2515, 2517, 470, 15, 13], [2518, 2525, 471, 15, 14], [2526, 2530, 472, 15, 15], [2530, 2533, 473, 15, 16], [2534, 2541, 474, 15, 17], [2542, 2545, 475, 15, 18], [2546, 2552, 476, 15, 19]]},
        'Arg2': {'CharacterSpanList': [[2554, 2573]], 'RawText': None, 'TokenList': [[2554, 2558, 478, 16, 0], [2559, 2563, 479, 16, 1], [2563, 2564, 480, 16, 2], [2565, 2566, 481, 16, 3], [2566, 2569, 482, 16, 4], [2570, 2573, 483, 16, 5]]},
        'Connective': {'CharacterSpanList': [], 'RawText': None, 'TokenList': []},
        'Punctuation': {'CharacterSpanList': [], 'RawText': None, 'TokenList': [], 'PunctuationType': ''},
        'DocID': 'wsj_1000',
        'ID': 14888,
        'Sense': ['Comparison.Contrast'],
        'Type': 'Implicit',
    }
    t_rel2 = t_rel1.copy()
    t_rel2['Sense'] = []
    t_rel2['Type'] = ""

    relations = load_relations_gold(dataset_dir, with_senses=True, with_rawtext=False, doc_ids=[doc_id], filter_types=filter_types, filter_senses=filter_senses)
    assert t_rel0_fail_id not in relations
    rel1 = relations[t_rel1['ID']]
    for span in ['Arg1', 'Arg2', 'Connective', 'Punctuation']:
        for k in ['CharacterSpanList', 'RawText', 'TokenList']:
            assert rel1[span][k] == t_rel1[span][k], (span, k)
    assert rel1['Punctuation']['PunctuationType'] == t_rel1['Punctuation']['PunctuationType']
    assert rel1 == t_rel1

    relationsnos = load_relations_gold(dataset_dir, with_senses=False, doc_ids=[doc_id], filter_types=filter_types, filter_senses=filter_senses)
    assert t_rel0_fail_id not in relations
    rel2 = relationsnos[t_rel2['ID']]
    for span in ['Arg1', 'Arg2', 'Connective', 'Punctuation']:
        for k in ['CharacterSpanList', 'RawText', 'TokenList']:
            assert rel2[span][k] == t_rel2[span][k], (span, k)
    assert rel2['Punctuation']['PunctuationType'] == t_rel2['Punctuation']['PunctuationType']
    assert rel2 == t_rel2

if __name__ == '__main__':
    import pytest
    pytest.main(['-s', __file__])
