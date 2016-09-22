#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0103
"""
Process shallow discourse relations from CoNLL16st corpus (from `relations.json` or `relations-no-senses.json`).
"""
__author__ = "GW [http://gw.tnode.com/] <gw.2016@tnode.com>"
__license__ = "GPLv3+"

from files import load_parses, load_raws, load_relations_gold
from words import get_word_metas


def rtsip_to_tag(rel_type, rel_sense, rel_id, rel_part):
    """Convert relation type, sense, id, and part to tag."""

    rel_tag = ":".join([rel_type, rel_sense, str(rel_id), rel_part])
    return rel_tag


def tag_to_rtsip(tag):
    """Convert tag to relation type, sense, id, and part."""

    rel_type, rel_sense, rel_id, rel_part = tag.split(":")
    return rel_type, rel_sense, int(rel_id), rel_part


def filter_tags(tags, prefixes=None):
    """Filter list of relation tags matching specified prefixes."""

    if prefixes is not None:
        # filter by specified relation tag prefixes
        tags = tuple( t  for t in tags if any(( t.startswith(p)  for p in prefixes )) )
    return tags


def strip_sense_level(rel_sense, level=None):
    """Strip relation sense to top level."""

    if level is not None:
        rel_sense = ".".join(rel_sense.split(".")[:level])
    return rel_sense


def get_rel_parts(relations_gold):
    """Extract only discourse relation parts/spans of token ids by relation id from CoNLL16st corpus.

        rel_parts[14905] = {
            'Arg1': (879, 880, 881, 882, 883, 884, 885, 886),
            'Arg1Len': 46,
            'Arg2': (877, 889, 890, 891, 892, 893, 894),
            'Arg2Len': 36,
            'Connective': (878, 888),
            'ConnectiveLen': 6,
            'Punctuation': (),
            'PunctuationLen': 0,
            'PunctuationType': '',
            'DocID': 'wsj_1000',
            'ID': 14905,
            'TokenMin': 877,
            'TokenMax': 894,
            'TokenCount': 17,
        }
    """

    rel_parts = {}
    for rel_id, gold in relations_gold.iteritems():
        doc_id = gold['DocID']
        punct_type = gold['Punctuation']['PunctuationType']

        # short token lists from detailed/gold format to only token id
        arg1_list = tuple( t[2]  for t in gold['Arg1']['TokenList'] )
        arg2_list = tuple( t[2]  for t in gold['Arg2']['TokenList'] )
        conn_list = tuple( t[2]  for t in gold['Connective']['TokenList'] )
        punct_list = tuple( t[2]  for t in gold['Punctuation']['TokenList'] )
        all_list = sum([list(arg1_list), list(arg2_list), list(conn_list), list(punct_list)], [])

        # character lengths of parts
        arg1_len = sum(( (e - b)  for b, e in gold['Arg1']['CharacterSpanList'] ))
        arg2_len = sum(( (e - b)  for b, e in gold['Arg2']['CharacterSpanList'] ))
        conn_len = sum(( (e - b)  for b, e in gold['Connective']['CharacterSpanList'] ))
        punct_len = sum(( (e - b)  for b, e in gold['Punctuation']['CharacterSpanList'] ))

        # save relation parts
        rel = {
            'Arg1': arg1_list,
            'Arg1Len': arg1_len,
            'Arg2': arg2_list,
            'Arg2Len': arg2_len,
            'Connective': conn_list,
            'ConnectiveLen': conn_len,
            'Punctuation': punct_list,
            'PunctuationLen': punct_len,
            'PunctuationType': punct_type,
            'DocID': doc_id,
            'ID': rel_id,
            'TokenMin': min(all_list),
            'TokenMax': max(all_list),
            'TokenCount': len(all_list),
        }
        rel_parts[rel_id] = rel
    return rel_parts


def get_rel_types(relations_gold, filter_types=None):
    """Extract discourse relation types by relation id from CoNLL16st corpus.

        rel_types[14905] = "Explicit"
    """

    rel_types = {}
    for rel_id, gold in relations_gold.iteritems():
        rel_type = gold['Type']
        if filter_types and rel_type not in filter_types:
            continue
        rel_types[rel_id] = rel_type
    return rel_types


def get_rel_senses(relations_gold, level=None, filter_senses=None):
    """Extract first discourse relation senses by relation id from CoNLL16st corpus.

        rel_senses[14905] = "Contingency.Condition"
    """

    rel_senses = {}
    for rel_id, gold in relations_gold.iteritems():
        sfirst = gold['Sense'][0]  # only first sense
        if filter_senses and sfirst not in filter_senses:
            continue
        sfirst = strip_sense_level(sfirst, level)  # strip to top level senses
        rel_senses[rel_id] = sfirst
    return rel_senses


def get_rel_senses_all(relations_gold, level=None, filter_senses=None):
    """Extract all discourse relation senses by relation id from CoNLL16st corpus.

        rel_senses_all[14905] = ("Contingency.Condition")
    """
    if filter_senses is None:
        filter_senses = ()

    rel_senses_all = {}
    for rel_id, gold in relations_gold.iteritems():
        slist = gold['Sense']
        slist = [ s for s in slist if s not in filter_senses ]
        slist = [ strip_sense_level(s, level) for s in slist ]  # strip to top level senses
        rel_senses_all[rel_id] = tuple(slist)
    return rel_senses_all


def add_relation_tags(word_metas, rel_types, rel_senses):
    """Add discourse relation tags to metadata of words/tokens.

        word_metas['wsj_1000'][0] = {
            ...
            'RelationTags': ("Explicit:Expansion.Conjunction:14890:Arg1",),
        }
    """

    for doc_id in word_metas:
        for meta in word_metas[doc_id]:
            tags = []
            for rel_id, rel_part in zip(meta['RelationIDs'], meta['RelationParts']):
                if rel_id not in rel_types or rel_id not in rel_senses:
                    continue  # skip missing relations

                rel_type = rel_types[rel_id]
                rel_sense_all = rel_senses[rel_id]
                if isinstance(rel_sense_all, str):  # only first sense
                    rel_sense_all = (rel_sense_all,)
                for rel_sense in rel_senses[rel_id]:
                    tags.append(rtsip_to_tag(rel_type, rel_sense, rel_id, rel_part))

            # save to metadata
            meta['RelationTags'] = tuple(tags)


### Tests

def test_rel_parts():
    dataset_dir = "./conll16st-en-trial"
    t_rel0 = {
        'Arg1': (879, 880, 881, 882, 883, 884, 885, 886),
        'Arg1Len': 46,
        'Arg2': (877, 889, 890, 891, 892, 893, 894),
        'Arg2Len': 36,
        'Connective': (878, 888),
        'ConnectiveLen': 6,
        'Punctuation': (),
        'PunctuationLen': 0,
        'PunctuationType': '',
        'DocID': 'wsj_1000',
        'ID': 14905,
        'TokenMin': 877,
        'TokenMax': 894,
        'TokenCount': 17,
    }

    relations_gold = load_relations_gold(dataset_dir)
    rel_parts = get_rel_parts(relations_gold)
    rel0 = rel_parts[t_rel0['ID']]
    assert rel0 == t_rel0

def test_rel_types():
    dataset_dir = "./conll16st-en-trial"
    t_rel0_id = 14905
    t_rel0 = 'Explicit'

    relations_gold = load_relations_gold(dataset_dir)
    rel_types = get_rel_types(relations_gold)
    rel0 = rel_types[t_rel0_id]
    assert rel0 == t_rel0

def test_rel_senses():
    dataset_dir = "./conll16st-en-trial"
    t_rel0_id = 14905
    t_rel0 = 'Contingency.Condition'
    t_rel1_id = 14905
    t_rel1 = 'Contingency'

    relations_gold = load_relations_gold(dataset_dir)
    rel_senses = get_rel_senses(relations_gold)
    rel0 = rel_senses[t_rel0_id]
    assert rel0 == t_rel0

    relations_gold = load_relations_gold(dataset_dir)
    rel_senses = get_rel_senses(relations_gold, level=1)
    rel1 = rel_senses[t_rel1_id]
    assert rel1 == t_rel1

def test_rel_senses_all():
    dataset_dir = "./conll16st-en-trial"
    t_rel0_id = 14905
    t_rel0 = ('Contingency.Condition',)
    t_rel1_id = 14905
    t_rel1 = ('Contingency',)

    relations_gold = load_relations_gold(dataset_dir)
    rel_senses = get_rel_senses_all(relations_gold)
    rel0 = rel_senses[t_rel0_id]
    assert rel0 == t_rel0

    relations_gold = load_relations_gold(dataset_dir)
    rel_senses = get_rel_senses_all(relations_gold, level=1)
    rel1 = rel_senses[t_rel1_id]
    assert rel1 == t_rel1

def test_relation_tags():
    dataset_dir = "./conll16st-en-trial"
    doc_id = "wsj_1000"
    t_meta0_id = 0
    t_meta0_tags = ('Explicit:Expansion.Conjunction:14890:Arg1',)
    t_meta1_id = 894
    t_meta1_tags = ('Explicit:Comparison.Concession:14904:Arg2', 'Explicit:Contingency.Condition:14905:Arg2')
    t_meta2_id = 895
    t_meta2_tags = ()

    parses = load_parses(dataset_dir)
    raws = load_raws(dataset_dir, [doc_id])
    word_metas = get_word_metas(parses, raws)
    relations_gold = load_relations_gold(dataset_dir)
    rel_types = get_rel_types(relations_gold)
    rel_senses = get_rel_senses(relations_gold)
    add_relation_tags(word_metas, rel_types, rel_senses)
    assert word_metas[doc_id][t_meta0_id]['RelationTags'] == t_meta0_tags
    assert word_metas[doc_id][t_meta1_id]['RelationTags'] == t_meta1_tags
    assert word_metas[doc_id][t_meta2_id]['RelationTags'] == t_meta2_tags

if __name__ == '__main__':
    import pytest
    pytest.main(['-s', __file__])
