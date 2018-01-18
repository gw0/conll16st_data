#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0103,W0621
"""Print basic statistics of CoNLL 2016 datasets."""

from .load import Conll16stDataset


def count_types(data):
    print("\nTypes:")

    counts = {}
    for rel_id in data['rel_ids']:
        rel_type = data['rel_types'][rel_id]
        try:
            counts[rel_type] += 1
        except KeyError:
            counts[rel_type] = 1

    for name, count in sorted(counts.items(), key=lambda a: a[0]):
        print("- {}: {}".format(name, count))


def count_senses(data):
    print("\nSenses:")

    counts = {}
    for rel_id in data['rel_ids']:
        rel_senses = data['rel_senses'][rel_id]
        for s in rel_senses:
            try:
                counts[s] += 1
            except KeyError:
                counts[s] = 1

    for name, count in sorted(counts.items(), key=lambda a: a[0]):
        print("- {}: {}".format(name, count))

def count_tsenses(data):
    print("\nSenses with prepended types:")

    counts = {}
    for rel_id in data['rel_ids']:
        rel_type = data['rel_types'][rel_id]
        rel_senses = data['rel_senses'][rel_id]
        for s in rel_senses:
            k = "{}:{}".format(rel_type, s)
            try:
                counts[k] += 1
            except KeyError:
                counts[k] = 1

    for name, count in sorted(counts.items(), key=lambda a: a[1], reverse=True):
        print("- {}: {}".format(name, count))


if __name__ == '__main__':
    import sys
    data_dir = sys.argv[1]

    print("load dataset '{}'".format(data_dir))
    data = Conll16stDataset(data_dir, with_rel_senses_all=True)
    print(data.summary())

    count_types(data)
    count_senses(data)
    count_tsenses(data)
    print("")

