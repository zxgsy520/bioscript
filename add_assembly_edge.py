#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import gzip
import logging
import argparse

LOG = logging.getLogger(__name__)

__version__ = "1.1.0"
__author__ = ("Xingguo Zhang",)
__email__ = "113178210@qq.com"
__all__ = []


def read_fasta(file):
    '''Read fasta file'''

    if file.endswith(".gz"):
        fp = gzip.open(file)
    elif file.endswith(".fasta") or file.endswith(".fa"):
        fp = open(file)
    else:
        raise Exception("%r file format error" % file)

    seq = ''

    for line in fp:
        if type(line) == type(b''):
            line = line.decode('utf-8')
        line = line.strip()

        if not line:
            continue
        if not seq:
            seq += "%s\n" % line.strip(">").split()[0]
            continue
        if line.startswith(">"):
            line = line.strip(">").split()[0]
            seq = seq.split('\n')

            yield seq[0], seq[1]
            seq = ''
            seq += "%s\n" % line
        else:
            seq += line

    seq = seq.split('\n')
    if len(seq)==2:
        yield seq[0], seq[1]


def read_fastq(file):
    '''Read fastq file'''

    if file.endswith(".gz"):
        fp = gzip.open(file)
    elif file.endswith(".fastq") or file.endswith(".fq"):
        fp = open(file)
    else:
        raise Exception("%r file format error" % file)

    seq = ''

    for line in fp:
        if type(line) == type(b''):
            line = line.decode('utf-8')
        line = line.strip()

        if not line:
            continue
        if not seq:
            seq += "%s\n" % line.strip("@").split()[0]
            continue
        if line.startswith('@'):
            line = line.strip("@").split()[0]
            seq = seq.split('\n')

            yield seq[0], seq[1]
            seq = ''
            seq = "%s\n" % line
        else:
            seq += "%s\n" % line

    if len(seq.split('\n'))==5:
        seq = seq.split('\n')
        yield seq[0], seq[1]


def add_assembly_edge(genome):

    if genome.endswith(".fastq") or genome.endswith(".fq") or genome.endswith(".fastq.gz") or genome.endswith(".fq.gz"):
        fh = read_fastq(genome)
    elif genome.endswith(".fasta") or genome.endswith(".fa") or genome.endswith(".fasta.gz") or genome.endswith(".fa.gz"):
        fh = read_fasta(genome)
    else:
        raise Exception("%r file format error" % genome)

    for seqid,seq in fh:
        print(">%s [topology=circular] [completeness=complete]\n%s%s" % (seqid, seq, seq[:5500]))

    return 0


def add_args(parser):

    parser.add_argument('fasta', help='')
    return parser


def main():
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.INFO,
        format="[%(levelname)s] %(message)s"
    )

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
name:
    add_assembly_edge.py Add overlap to the ringed genome
attention:
    add_assembly_edge.py assembly.fasta >assembly_new.fasta

version: %s
contact:  %s <%s>\
    """ % (__version__, " ".join(__author__), __email__))

    parser = add_args(parser)
    args = parser.parse_args()

    add_assembly_edge(args.fasta)


if __name__ == "__main__":
    main()
