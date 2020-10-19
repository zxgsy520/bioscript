#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import logging
import argparse

LOG = logging.getLogger(__name__)

__version__ = "1.2.0"
__author__ = ("Xingguo Zhang",)
__email__ = "113178210@qq.com"
__all__ = []


def read_tsv(file, sep=None):

    LOG.info("reading message from %r" % file)

    for line in open(file):
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        yield line.split(sep)


def gmk2pb(string):

    string = string.lower().strip()

    if string.endswith('g') or string.endswith('gb'):
        base = string.split('g')[0]
        base = float(base)*1e+09
    elif string.endswith('m') or string.endswith('mb'):
        base = string.split('m')[0]
        base = float(base)*1e+06
    elif string.endswith('k') or string.endswith('kb'):
        base = string.split('k')[0]
        base = float(base)*1e+03
    else:
        base = float(string)

    return int(base)


def recover_contig(file, minlen="1.5Mb"):

    seqid = set()
    minlen = gmk2pb(minlen)

    for line in read_tsv(file, '\t'):
        if line[0]=='H':
            continue
        if line[0]=='S':
            if len(line[2])>=minlen:
                seqid.add(line[1])
            continue
        if line[0]=='L':
            if (line[1] in seqid) or (line[3] in seqid):
                seqid.add(line[1])
                seqid.add(line[3])
            continue

    return seqid


def filter_gfa(file, minlen):

    seqid = recover_contig(file, minlen)

    for line in read_tsv(file, '\t'):
        if line[0] not in ['S', 'L']:
            print('\t'.join(line))
            continue
        if line[0]=='S':
            if line[1] not in seqid:
                continue
            print('\t'.join(line))
        else:
            if (line[1] not in seqid) and (line[3] not in seqid):
                continue
            print('\t'.join(line))
    return 0


def add_help(parser):

    parser.add_argument('gfa',
        help='Input file.')
    parser.add_argument('--minlen', metavar='STR', type=str, default='1.5mb',
        help='Minimum length of filtering, default=1.5mb.')

    return parser


def main():

    logging.basicConfig(
        stream=sys.stderr,
        level=logging.INFO,
        format="[%(levelname)s] %(message)s"
    )
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''
name:
    filter_gfa.py Filter the assembled gfa file
attention:
    filter_gfa.py file.gfa --minlen 1.5mb >new.gfa
version: %s
contact:  %s <%s>\
        ''' % (__version__, ' '.join(__author__), __email__))

    args = add_help(parser).parse_args()

    filter_gfa(args.gfa, args.minlen)


if __name__ == "__main__":

    main()
