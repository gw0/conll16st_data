#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0103
"""
Process words/tokens from CoNLL16st corpus (from `parses.json` and `raw/`).
"""
__author__ = "GW [http://gw.tnode.com/] <gw.2016@tnode.com>"
__license__ = "GPLv3+"

import re

from files import load_parses, load_raws


def get_words(parses):
    """Extract only words/tokens by document id and token id from CoNLL16st corpus.

        words["wsj_1000"] = ["Kemper", "Financial", "Services", "Inc.", ",", "charging", ...]
    """

    words = {}
    for doc_id in parses:
        words[doc_id] = []
        for sentence_dict in parses[doc_id]['sentences']:
            for token in sentence_dict['words']:
                word = token[0]
                words[doc_id].append(word)
    return words


def get_pos_tags(parses):
    """Extract only part-of-speech tags by document id and token id from CoNLL16st corpus.

        pos_tags["wsj_1000"] = ["NNP", "NNP", "NNPS", "NNP", ",", "VBG", ...]
    """

    pos_tags = {}
    for doc_id in parses:
        pos_tags[doc_id] = []
        for sentence_dict in parses[doc_id]['sentences']:
            for token in sentence_dict['words']:
                pos_tags[doc_id].append(token[1]['PartOfSpeech'])
    return pos_tags


def get_word_metas(parses, raws):
    """Extract other metadata of words/tokens by document id and token id from CoNLL16st corpus.

        word_metas['wsj_1000'][0] = {
            'Text': 'Kemper',
            'DocID': 'wsj_1000',
            'ParagraphID': 0,
            'SentenceID': 0,
            'SentenceOffset': 0,
            'TokenID': 0,
            'RelationIDs': (14890,),
            'RelationParts': ('Arg1',),
        }
    """
    paragraph_sep="^\W*\n\n\W*$"  # regex for paragraph separator
    linker_split = "_"
    linker_to_span = {"arg1": 'Arg1', "arg2": 'Arg2', "conn": 'Connective', "punct": 'Punctuation'}

    word_metas = {}
    for doc_id in parses:
        paragraph_id = 0  # paragraph number within document
        sentence_id = 0  # sentence number within document
        token_id = 0  # token number within document
        prev_token_end = 0  # previous token last character offset

        word_metas[doc_id] = []
        for sentence_dict in parses[doc_id]['sentences']:
            sentence_offset = token_id  # first token number in sentence

            for token in sentence_dict['words']:
                word = token[0]

                # check for paragraph separator
                if doc_id not in raws:
                    raise Exception("Missing raw text ({})".format(doc_id))
                skipped_str = raws[doc_id][prev_token_end:token[1]['CharacterOffsetBegin']]
                if re.match(paragraph_sep, skipped_str, flags=re.MULTILINE):
                    paragraph_id += 1
                prev_token_end = token[1]['CharacterOffsetEnd']

                # discourse relations metadata
                rel_ids = []
                rel_spans = []
                for linker in token[1]['Linkers']:
                    linker_span, rel_id = linker.rsplit(linker_split, 1)
                    rel_ids.append(int(rel_id))
                    rel_spans.append(linker_to_span[linker_span])

                # save metadata
                meta = {
                    'Text': word,
                    'DocID': doc_id,
                    'ParagraphID': paragraph_id,
                    'SentenceID': sentence_id,
                    'SentenceOffset': sentence_offset,
                    'TokenID': token_id,
                    'RelationIDs': tuple(rel_ids),
                    'RelationParts': tuple(rel_spans),
                }
                word_metas[doc_id].append(meta)
                token_id += 1
            sentence_id += 1
    return word_metas


### Tests

def test_words():
    dataset_dir = "./conll16st-en-trial"
    t_doc_id = "wsj_1000"
    t_words = ["Kemper", "Financial", "Services", "Inc.", ",", "charging"]
    t_words_end = ["more", "important", "."]

    parses = load_parses(dataset_dir)
    words = get_words(parses)
    assert words[t_doc_id][:len(t_words)] == t_words
    assert words[t_doc_id][-len(t_words_end):] == t_words_end

def test_pos_tags():
    dataset_dir = "./conll16st-en-trial"
    t_doc_id = "wsj_1000"
    t_pos_tags = ["NNP", "NNP", "NNPS", "NNP", ",", "VBG"]
    t_pos_tags_end = ["RBR", "JJ", "."]

    parses = load_parses(dataset_dir)
    pos_tags = get_pos_tags(parses)
    assert pos_tags[t_doc_id][:len(t_pos_tags)] == t_pos_tags
    assert pos_tags[t_doc_id][-len(t_pos_tags_end):] == t_pos_tags_end

def test_word_metas():
    dataset_dir = "./conll16st-en-trial"
    doc_id = "wsj_1000"
    t_meta0 = {
        'Text': 'Kemper',
        'DocID': 'wsj_1000',
        'ParagraphID': 0,
        'SentenceID': 0,
        'SentenceOffset': 0,
        'TokenID': 0,
        'RelationIDs': (14890,),
        'RelationParts': ('Arg1',),
    }
    t_meta1 = {
        'Text': 'important',
        'DocID': 'wsj_1000',
        'ParagraphID': 13,
        'SentenceID': 32,
        'SentenceOffset': 877,
        'TokenID': 894,
        'RelationIDs': (14904, 14905),
        'RelationParts': ('Arg2', 'Arg2'),
    }
    t_meta2 = {
        'Text': '.',
        'DocID': 'wsj_1000',
        'ParagraphID': 13,
        'SentenceID': 32,
        'SentenceOffset': 877,
        'TokenID': 895,
        'RelationIDs': (),
        'RelationParts': (),
    }

    parses = load_parses(dataset_dir)
    raws = load_raws(dataset_dir, [doc_id])
    word_metas = get_word_metas(parses, raws)
    assert word_metas[doc_id][t_meta0['TokenID']] == t_meta0
    assert word_metas[doc_id][t_meta1['TokenID']] == t_meta1
    assert word_metas[doc_id][t_meta2['TokenID']] == t_meta2

if __name__ == '__main__':
    import pytest
    pytest.main(['-s', __file__])
