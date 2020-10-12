#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
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
        fa = gzip.open(file)
    elif file.endswith(".fasta") or file.endswith(".fa"):
        fa = open(file)
    else:
        raise Exception("%r file format error" % file)

    seq = ''
    for line in fa:
        if type(line) == type(b''):
            line = line.decode('utf-8')
        line = line.strip()

        if not line:
            continue
        if line.startswith(">"):
            seq = seq.split('\n')
            if len(seq)==2:
                yield seq[0], seq[1]
            seq = ''
            line = line.strip(">").split()[0]
            seq += "%s\n" % line
            continue
        seq += line

    seq = seq.split('\n')
    if len(seq)==2:
        yield seq[0], seq[1]
    fa.close()


def read_fastq(file):
    '''Read fastq file'''

    if file.endswith(".gz"):
        fp = gzip.open(file, 'r')
    elif file.endswith(".fastq") or file.endswith(".fq"):
        fp = open(file)
    else:
        raise Exception("%r file format error" % file)

    seq = []
    for line in fp:
        if type(line) == type(b''):
            line = line.decode('utf-8')
        line = line.strip()

        if not line:
            continue
        if line.startswith("@") and (len(seq)==0 or len(seq)>=5):
            seq = []
            seq.append(line.strip("@").split()[0])
            continue
        if line.startswith("@") and len(seq)==4:
            yield seq[0], seq[1]
            seq = []
            seq.append(line.strip("@").split()[0])
            continue
        seq.append(line)

    if len(seq)==4:
        yield seq[0], seq[1]
    fp.close()


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


def check_path(path):

    path = os.path.abspath(path)

    if not os.path.exists(path):
        msg = "File not found '{path}'".format(**locals())
        LOG.error(msg)
        raise Exception(msg)

    return path


def allot_base(file, name, base):

    n = 0
    lable = 1
    base = gmk2pb(base)
    fname = "%s.%s.fa" % (name, str(lable))
    output = open(fname, 'w')

    if file.endswith(".fastq") or file.endswith(".fq") or file.endswith(".fastq.gz") or file.endswith(".fq.gz"):
        fh = read_fastq(file)
    elif file.endswith(".fasta") or file.endswith(".fa") or file.endswith(".fasta.gz") or file.endswith(".fa.gz"):
        fh = read_fasta(file)
    else:
        raise Exception("%r file format error" % file)

    for seqid, seq in fh:
        if n>=base:
            output.close()
            fname = check_path(fname)
            print(fname)
            n = len(seq)
            lable += 1
            fname = "%s.%s.fa" % (name, str(lable))
            output = open(fname, 'w')
            output.write(">%s\n%s\n" % (seqid, seq))
        else:
            output.write(">%s\n%s\n" % (seqid, seq))
            n += len(seq)

    output.close()
    fname = check_path(fname)
    print(fname)


def add_help(parser):

    parser.add_argument('input',
        help='Input file.')
    parser.add_argument('-b', '--base', metavar='STR', type=str, default='10mb',
        help='Split base size, default=10mb.')
    parser.add_argument('-n', '--name', metavar='STR', type=str, default='out',
        help='Input file prefix name.')

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
    allot_base.py Split sequence file based on base amount

attention:
    allot_base.py file.fastq
    allot_base.py file.fasta -n out -b 10mb >split.list

version: %s
contact:  %s <%s>\
        ''' % (__version__, ' '.join(__author__), __email__))

    args = add_help(parser).parse_args()

    allot_base(args.input, args.name, args.base)


if __name__ == "__main__":

    main()
