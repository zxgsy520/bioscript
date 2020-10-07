#!/usr/bin/env python
#coding:utf-8

import os
import re
import sys
import pysam
import logging
import argparse


LOG = logging.getLogger(__name__)

__version__ = "1.0.0"
__author__ = ("Xingguo Zhang",)
__email__ = "113178210@qq.com"
__all__ = []


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False


def gmk2pb(string):

    string = string.strip().lower()
    size = 0

    if string.endswith('gb') or string.endswith('g'):
        string = string.split('g')[0]
        size = float(string)*1e9
    elif string.endswith('mb') or string.endswith('m'):
        string = string.split('m')[0]
        size = float(string)*1e6
    elif string.endswith('kb') or string.endswith('k'):
        string = string.split('k')[0]
        size = float(string)*1e3
    elif string.endswith('bp') or string.endswith('b') or is_number(string):
        string = string.split('b')[0]
        size = float(string)
    else:
        pass
#        raise Exception("%s format error" % string)

    return size


def filter_bam(file, ofile, minlen=500, minqv=0.8, tbase="500Mb"):

    tbase = gmk2pb(tbase)

    if file.endswith(".bam"):
        fh = pysam.AlignmentFile(file, "rb", check_sq=False)
    elif file.endswith(".sam"):
        fh = pysam.AlignmentFile(file, 'r')
    else:
        raise Exception("%r file format error" % file)

    fo = pysam.AlignmentFile(ofile, "wb", template=fh)
    n = 0
    print(tbase)

    for line in fh:
        if line.get_tag('rq')<minqv or len(line.seq)<minlen:
            continue
        n += len(line.seq)
        fo.write(line)
        
        if tbase and n>=tbase:
            break

    fh.close()
    fo.close()


def add_hlep_args(parser):

    parser.add_argument('bam',
        help='Input reads file, format(bam and sam).')
    parser.add_argument('-l', '--minlen', metavar='INT', type=int, default=500,
        help='Minimum read length for filtering, default=500.')
    parser.add_argument('-q', '--minqv', metavar='FLOAT', type=float, default=0.8,
        help='Filtered minimum read quality value, default=0.8.')
    parser.add_argument('-b', '--base', metavar='STR', type=str, default='500Mb',
        help='Number of bases reserved, default=500Mb.')
    parser.add_argument('-o', '--out', metavar='STR', type=str, default='out.bam',
        help='Output result file,default=out.bam.')

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
    filter_bam.py Filter the bam files sequenced by pacbio.

attention:
    filter_bam.py input.bam -o out.bam
version: %s
contact:  %s <%s>\
        ''' % (__version__, ' '.join(__author__), __email__))

    args = add_hlep_args(parser).parse_args()

    filter_bam(args.bam, args.out, args.minlen, args.minqv, args.base)


if __name__ == "__main__":

    main()
