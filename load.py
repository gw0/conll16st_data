#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0103
"""
Load CoNLL16st/CoNLL15st dataset.
"""
__author__ = "GW [http://gw.tnode.com/] <gw.2016@tnode.com>"
__license__ = "GPLv3+"

from files import load_parses, load_raws, load_relations_gold
from words import get_words, get_pos_tags, get_word_metas
from dependencies import get_dependencies
from parsetrees import get_parsetrees
from relations import get_rel_parts, get_rel_types, get_rel_senses, get_rel_senses_all, add_relation_tags


def load_all(dataset_dir, doc_ids=None, filter_types=None, filter_senses=None, filter_fn=None, with_rel_senses_all=False):
    """Load whole CoNLL16st dataset by document id."""

    # load all provided files untouched
    parses = load_parses(dataset_dir, doc_ids=doc_ids)
    doc_ids = sorted(parses.keys())
    raws = load_raws(dataset_dir, doc_ids=doc_ids)
    relations_gold = load_relations_gold(dataset_dir, doc_ids=doc_ids, with_senses=True, filter_types=filter_types, filter_senses=filter_senses, filter_fn=filter_fn)
    if relations_gold:
        relationsnos_gold = relations_gold
    else:
        relationsnos_gold = load_relations_gold(dataset_dir, doc_ids=doc_ids, with_senses=False, filter_types=filter_types, filter_senses=filter_senses, filter_fn=filter_fn)

    # extract data by document id and token id
    words = get_words(parses)
    pos_tags = get_pos_tags(parses)
    word_metas = get_word_metas(parses, raws)

    # extract data by document id and token id pairs
    dependencies = get_dependencies(parses)

    # extract data by document id
    parsetrees = get_parsetrees(parses)

    # extract data by relation id
    rel_parts = get_rel_parts(relationsnos_gold)
    rel_ids = sorted(rel_parts.keys())
    rel_types = get_rel_types(relations_gold)
    if with_rel_senses_all:
        rel_senses = get_rel_senses_all(relations_gold)
    else:
        rel_senses = get_rel_senses(relations_gold)

    # add extra fields
    add_relation_tags(word_metas, rel_types, rel_senses)

    return doc_ids, words, word_metas, pos_tags, dependencies, parsetrees, rel_ids, rel_parts, rel_types, rel_senses, relations_gold


class Conll16stDataset(dict):
    """CoNLL16st dataset holder as dict."""

    def __init__(self, dataset_dir, lang='?', doc_ids=None, filter_types=None, filter_senses=None, filter_fn=None, with_rel_senses_all=False):
        self.dataset_dir = dataset_dir
        self.filter_types = filter_types
        self.filter_senses = filter_senses
        self.filter_fn = filter_fn

        self['lang'] = lang
        self['doc_ids'], self['words'], self['word_metas'], self['pos_tags'], self['dependencies'], self['parsetrees'], self['rel_ids'], self['rel_parts'], self['rel_types'], self['rel_senses'], self['relations_gold'] = load_all(dataset_dir, doc_ids=doc_ids, filter_types=filter_types, filter_senses=filter_senses, filter_fn=filter_fn, with_rel_senses_all=with_rel_senses_all)
        if not self['doc_ids']:
            raise IOError("Failed to load dataset ({})!".format(dataset_dir))

    def summary(self):
        return "lang: {}, doc_ids: {}, words: {}, rel_ids: {}, relation tokens: {}".format(self['lang'], len(self['doc_ids']), sum([ len(s) for s in self['words'].itervalues() ]), len(self['rel_ids']), sum([ self['rel_parts'][rel_id]['TokenCount'] for rel_id in self['rel_parts'] ]))
