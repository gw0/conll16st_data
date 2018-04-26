#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0103
"""
Tool for converting word sequences of text spans from CoNLL16st corpus to JSONL format.
"""
__author__ = "GW [http://gw.tnode.com/] <gw.2016@tnode.com>"
__license__ = "GPLv3+"

import argparse
import codecs
import json
import logging

from conll16st_data.load import Conll16stDataset


# constants for CoNLL16st datasets
RELATION_TYPES = ['Explicit', 'Implicit', 'AltLex', 'EntRel', 'NoRel']
EN_SENSES_DEFAULT = 'Expansion.Conjunction'
EN_SENSES = [
    'Temporal.Asynchronous.Precedence',
    'Temporal.Asynchronous.Succession',
    'Temporal.Synchrony',
    'Contingency.Cause.Reason',
    'Contingency.Cause.Result',
    'Contingency.Condition',
    'Comparison.Contrast',
    'Comparison.Concession',
    'Expansion.Conjunction',
    'Expansion.Instantiation',
    'Expansion.Restatement',
    'Expansion.Alternative',
    'Expansion.Alternative.Chosen alternative',
    'Expansion.Exception',
    'EntRel',
]
ZH_SENSES_DEFAULT = 'Conjunction'
ZH_SENSES = [
    'Alternative',
    'Causation',
    'Conditional',
    'Conjunction',
    'Contrast',
    'EntRel',
    'Expansion',
    'Progression',
    'Purpose',
    'Temporal',
]


def encode_target(rel_type, rel_sense_all, rel_part=None, rel_id=None, lang='en'):
    """Encode multi-label target value for prediction."""

    # predict only valid senses
    SENSES = EN_SENSES
    if lang == 'zh':
        SENSES = ZH_SENSES
    senses = []
    for s in rel_sense_all:
        if s in SENSES:
            senses.append(s)
            continue
        # for partial senses mark all subsenses
        for k in SENSES:
            if k.startswith(s):
                senses.append(s)
    senses.sort(key=lambda s: -len(s))
    # only sense
    #return senses
    # with prepended type
    return tuple("{}:{}".format(rel_type, s)  for s in senses)
    # only first sense (single-label classification)
    #return senses[0]

def target_agg_labels(dataset):
    """Extract aggregated target labels for multi-label classification."""

    target = {}
    for rel_id, rel_sense_all in dataset['rel_senses'].items():
        rel_type = dataset['rel_types'][rel_id]
        target[rel_id] = encode_target(rel_type, rel_sense_all, rel_id=rel_id, lang=dataset['lang'])
    return target

def extract_sample(dataset, rel_id):
    """Extract training sample with word sequences of text spans."""

    doc_id = dataset['rel_parts'][rel_id]['DocID']
    doc_len = len(dataset['words'][doc_id])

    # original word sequences of text spans
    def map_to_words(poss):
        return [ dataset['words'][doc_id][i] for i in poss ]
    arg1_words = map_to_words(dataset['rel_parts'][rel_id]['Arg1'])
    arg2_words = map_to_words(dataset['rel_parts'][rel_id]['Arg1'])
    conn_words = map_to_words(dataset['rel_parts'][rel_id]['Connective'])
    punc_words = map_to_words(dataset['rel_parts'][rel_id]['Punctuation'])

    # gold labels
    try:
        target = dataset['target'][rel_id]
    except KeyError:
        target = []  # missing in blind datasets

    # extracted sample
    sample = {
        'doc_id': doc_id,
        'rel_id': rel_id,
        'arg1_words': arg1_words,
        'arg2_words': arg2_words,
        'conn_words': conn_words,
        'punc_words': punc_words,
        'gold_labels': target,
    }
    return sample


# parse arguments
argp = argparse.ArgumentParser(description=__doc__.strip().split("\n", 1)[0])
argp.add_argument('--dataset_dir', type=str, default="./conll16st-en-trial",
    help="CoNLL16st dataset directory to convert")
argp.add_argument('--output_jsonl', type=str, default="./conll16st-en-trial.jsonl",
    help="Converted output in JSONL format")
argp.add_argument('--lang', default="en",
    choices=["en", "zh"],
    help="dataset language (en/zh)")
args = argp.parse_args()

# configure logging
logging.basicConfig(format="[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M", level=logging.DEBUG)
log = logging.getLogger(__name__)

# load CoNLL16st dataset
filter_types = None  #['Implicit']

log.info("load dataset ({})".format(args.dataset_dir))
dataset = Conll16stDataset(args.dataset_dir, lang=args.lang, filter_types=filter_types, with_rel_senses_all=True)
dataset['target'] = target_agg_labels(dataset)
log.info("  " + dataset.summary())

# convert samples and save to JSONL format
log.info("convert ({})".format(args.output_jsonl))
with codecs.open(args.output_jsonl, 'w', encoding='utf8') as f:
    for rel_id in dataset['rel_ids']:
        sample = extract_sample(dataset, rel_id)
        f.write(json.dumps(sample, sort_keys=True, ensure_ascii=False))
        f.write("\n")

log.info("done")
