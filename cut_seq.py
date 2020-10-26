#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
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

    if file.endswith("fa.gz") or file.endswith("fasta.gz"):
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

        if not line or line.startswith("#"):
            continue
        if line.startswith(">"):
            if seq!='':
                yield seq.split('\n')
            seq = "%s\n" % line
            continue
        seq += line

    if seq!='':
        yield seq.split('\n')
    fp.close()


def read_fastq(file):
    '''Read fastq file'''
    if file.endswith(".fq.gz") or file.endswith(".fastq.gz"):
        fp = gzip.open(file)
    elif file.endswith(".fastq") or file.endswith(".fq"):
        fp = open(file)
    else:
        raise Exception("%r file format error" % file)

    seq = ''
    n = 0
    for line in fp:
        if type(line) == type(b''):
            line = line.decode('utf-8')
        line = line.strip()

        if not line or line.startswith("#"):
            continue
        n +=1
        seq += "%s\n" % line
        if n==4:
            n=0
            seq = seq.split('\n')
            yield seq[0], seq[1]
            seq = ''
    fp.close()


def read_fp(files, name, start ,end):

    seq_dict = {}

    if files.endswith(".fastq") or files.endswith(".fq") or files.endswith(".fastq.gz") or files.endswith(".fq.gz"):
        fh = read_fastq(files)
    else:
        fh = read_fasta(files)

    for id, seq in fh:
        id = id.replace('>','').replace('@','').split()[0]
        seq_dict[id] = seq

    if name in seq_dict:
        if int(end) <=1:
            end = len(seq_dict[name])
        seq_id = '{}_{}_{}'.format(name, start, end)
        #print(seq_dict[name])
        seq = seq_dict[name][int(start)-1:int(end)]
        print('>%s\n%s' % (seq_id, seq))
    else:
        LOG.info('Sequence %s does not exist, please confirm input.' % name)


def add_cut_help(parser):

    parser.add_argument('input',
        help='Input the fasta(q) sequence.')
    parser.add_argument('-id', '--id_name', metavar='STR', type=str, default=True,
        help='Input the cut sequence id.')
    parser.add_argument('-s', '--start', metavar='INT', type=int, default=1,
        help='Input the starting site of the cut.')
    parser.add_argument('-e', '--end', metavar='INT', type=int, default=1,
        help='Input cut-out termination site.')
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
    cut_seq -- Cut specific segments of a particular sequence

attention:
    cut_seq.  genen.fasta -id scf00001
    cut_seq  genen.fasta -id scf00001 --start 2 --end 2000
''')
    args = add_cut_help(parser).parse_args()

    read_fp(args.input, args.id_name, args.start ,args.end)


if __name__ == "__main__":

    main()
