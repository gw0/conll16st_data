#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0103
"""
Process parse trees from CoNLL16st corpus (from `parses.json`).
"""
__author__ = "GW [http://gw.tnode.com/] <gw.2016@tnode.com>"
__license__ = "GPLv3+"

import pyparsing

from files import load_parses


def get_parsetrees(parses):
    """Extract parse trees of token ids by document id from CoNLL16st corpus.

        # "( (S (NP (NNP Kemper) (NNP Financial) (NNPS Services)..." is represented as:
        parsetrees["wsj_1000"][0] = (u'S', (u'NP', (u'NNP', 0), (u'NNP', 1), (u'NNPS', 2), ...
    """
    sub_begin = "("
    sub_end = ")"
    m = {}  # mutable in helper function

    def _is_list(o, list_types=(list, tuple, set)):
        return any(( isinstance(o, t)  for t in list_types ))

    def _is_string(o, string_types=(str, unicode)):
        return any(( isinstance(o, t)  for t in string_types ))

    def _is_token_leaf(o):
        return len(o) == 2 and _is_string(o[0]) and not _is_list(o[1])

    def _replace_tokens(tree):
        if _is_list(tree):
            if _is_token_leaf(tree):  # leaf with token found
                tree[1] = m['token_id']
                m['token_id'] += 1
                return tuple(tree)
            else:
                return tuple( _replace_tokens(t)  for t in tree )
        else:
            return tree

    parsetrees = {}
    for doc_id in parses:
        m['token_id'] = 0  # token number within document

        parsetrees[doc_id] = []
        for sentence_dict in parses[doc_id]['sentences']:
            parsetree_str = sentence_dict['parsetree']

            # parse as list
            parsetree = pyparsing.nestedExpr(sub_begin, sub_end, ignoreExpr=None).parseString(parsetree_str).asList()

            # replace with token ids
            parsetree = _replace_tokens(parsetree[0])

            # save
            parsetrees[doc_id].append(parsetree)
    return parsetrees


### Tests

def test_parsetrees():
    dataset_dir = "./conll16st-en-trial"
    t_doc_id = "wsj_1000"
    t_s0_p0 = "S"
    t_s0_p1 = "NP"
    t_s0_p2 = ("NNP", 0)  #= "(NNP Kemper)"
    t_s0_p3 = ("NNP", 1)  #= "(NNP Financial)"
    t_s0_p4 = ("NNPS", 2)  #= "(NNPS Services)"
    t_s32_p0 = (".", 895) #= "(. .)"
    t_s32_p1 = ("JJ", 894)  #= "(JJ important)"
    t_s32_p2 = ("RBR", 893)  #= "(RBR more)"

    parses = load_parses(dataset_dir)
    parsetrees = get_parsetrees(parses)
    s0 = parsetrees[t_doc_id][0]
    assert s0[0][0] == t_s0_p0
    assert s0[0][1][0] == t_s0_p1
    assert s0[0][1][1] == t_s0_p2
    assert s0[0][1][2] == t_s0_p3
    assert s0[0][1][3] == t_s0_p4
    s32 = parsetrees[t_doc_id][32]
    assert s32[-1][-1] == t_s32_p0
    assert s32[-1][-2][-1][-1][-1] == t_s32_p1
    assert s32[-1][-2][-1][-1][-2][-1] == t_s32_p2

if __name__ == '__main__':
    import pytest
    pytest.main(['-s', __file__])
