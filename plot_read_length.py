#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import sys
import gzip
import logging
import argparse
import matplotlib
matplotlib.use('Agg')

from matplotlib import pyplot as plt


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
    fp.close()


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

    fp.close()


def stat_length(file):

    length = []

    if file.endswith(".fastq") or file.endswith(".fq") or file.endswith(".fastq.gz") or file.endswith(".fq.gz"):
        fh = read_fastq(file)
    elif file.endswith(".fasta") or file.endswith(".fa") or file.endswith(".fasta.gz") or file.endswith(".fa.gz"):
        fh = read_fasta(file)
    else:
        raise Exception("%r file format error" % file)

    for seq_id,seq in fh:
        length.append(len(seq))

    return length


def n50(lengths):

    sum_length = sum(lengths)
    accu_length = 0
    n = 0

    for i in sorted(lengths, reverse=True):
        accu_length += i
        if accu_length >= sum_length*0.5:
            n = i 
            break 

    return n


def plot_read_length(file, out, xmin=0, bins=50):

    length = stat_length(file)
    n50len = n50(length)
    xmax = n50len*2.5

    plt.style.use('ggplot')
    fig, ax = plt.subplots(figsize=(10, 6),)
#    ax.grid(color='w')
#    ax.patch.set_facecolor("#ffcfdc")
    ax.spines['top'].set_visible(False) #去掉上边框
    ax.spines['bottom'].set_visible(False) #去掉下边框
    ax.spines['left'].set_visible(False) #去掉左边框
    ax.spines['right'].set_visible(False) #去掉右边框

    ax.hist(length, bins=bins, range=(xmin, xmax), histtype='stepfilled', color="#cb416b", alpha=0.75)
    ax.set_xlim(xmin, xmax)

    font = {'weight': 'bold','size': 12,}
    ax.set_ylabel('Count', font)
    ax.set_xlabel('Length', font)
    plt.xticks()
    plt.savefig("%s.reads_length.pdf" % out)
    plt.savefig("%s.reads_length.png" % out, dpi=700) 


def add_hlep(parser):

    parser.add_argument('input',
        help='Input file.')
    parser.add_argument("--bins", metavar="INT", type=int, default=50,
        help="Bins to stat (default: 100).")
    parser.add_argument("--xmin", metavar="INT", type=int, default=0,
        help="Show the minimum read length (default: 0).")
    parser.add_argument('-o', '--out', metavar='STR',type=str, default="out",
        help='Out name')

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
    plot_read_length.py  Drawing the read length map via fastq or fasta files

attention:
    plot_read_length.py reads.fa
    plot_read_length.py reads.fq
''')
    args = add_hlep(parser).parse_args()
    plot_read_length(args.input, args.out, args.xmin, args.bins)


if __name__ == "__main__":

    main()
