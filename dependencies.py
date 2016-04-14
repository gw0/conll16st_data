#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0103
"""
Process word/token dependencies from CoNLL16st corpus (from `parses.json`).
"""
__author__ = "GW [http://gw.tnode.com/] <gw.2016@tnode.com>"
__license__ = "GPLv3+"

from files import load_parses


def get_dependencies(parses):
    """Extract word/token dependencies by document id and token id pairs from CoNLL16st corpus.

        # ["nn", "Inc.-4", "Kemper-1"] is represented as:
        dependencies["wsj_1000"][3][0] = "nn"
    """
    dep_split = "-"

    dependencies = {}
    for doc_id in parses:
        token_id = 0  # token number within document

        dependencies[doc_id] = {}
        dependencies[doc_id][-1] = {}  # for root governor (= -1)
        for sentence_dict in parses[doc_id]['sentences']:
            sentence_offset = token_id  # first token number in sentence

            for _ in sentence_dict['words']:  # for tokens as governor
                dependencies[doc_id][token_id] = {}
                token_id += 1

            for dependency, part1, part2 in sentence_dict['dependencies']:
                # governor of the dependency relation
                _, part1_id = part1.rsplit(dep_split, 1)
                if part1_id == "0":
                    part1_id = -1
                else:
                    part1_id = sentence_offset + int(part1_id) - 1

                # dependent of the dependency relation
                _, part2_id = part2.rsplit(dep_split, 1)
                if part2_id == "0":
                    part2_id = -1
                else:
                    part2_id = sentence_offset + int(part2_id) - 1

                # save dependency
                dependencies[doc_id][part1_id][part2_id] = dependency
    return dependencies


### Tests

def test_dependencies():
    dataset_dir = "./conll16st-en-trial"
    t_doc_id = "wsj_1000"
    t_dep0 = "root"
    t_dep0_governor = -1   #= "ROOT-0"
    t_dep0_dependent = 0 + 15  #= "cut-16"
    t_dep1 = "nn"
    t_dep1_governor = 0 + 3   #= "Inc.-4"
    t_dep1_dependent = 0 + 0  #= "Kemper-1"
    t_dep2 = "advmod"
    t_dep2_governor = 877 + 17   #= "important-18"
    t_dep2_dependent = 877 + 16  #= "more-17"

    parses = load_parses(dataset_dir)
    dependencies = get_dependencies(parses)
    assert dependencies[t_doc_id][t_dep0_governor][t_dep0_dependent] == t_dep0
    assert dependencies[t_doc_id][t_dep1_governor][t_dep1_dependent] == t_dep1
    assert dependencies[t_doc_id][t_dep2_governor][t_dep2_dependent] == t_dep2

if __name__ == '__main__':
    import pytest
    pytest.main(['-s', __file__])
