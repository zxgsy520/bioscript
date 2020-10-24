#!/usr/bin/env python
#coding:utf-8

import os
import re
import sys
import pysam
import logging
import argparse

LOG = logging.getLogger(__name__)

__version__ = "2.0.0"
__author__ = ("Xingguo Zhang",)
__email__ = "113178210@qq.com"
__all__ = []


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


def get_sample(file):

    name = file.split('/')[-1]

    if '--' in name:
        name = name.split('--')[1].split('.bam')[0]
    else:
        name = name.split('.')[0]

    return name


def filter_bam(file, qvalue=0.8, minlen=500, keep='1Gb'):

    if file.endswith(".bam"):
        fh = pysam.AlignmentFile(file, "rb", check_sq=False)
    elif file.endswith(".sam"):
        fh = pysam.AlignmentFile(file, 'r')
    else:
        raise Exception("%r file format error" % file)

    name = get_sample(file)
    fo = pysam.AlignmentFile("%s.clean.bam" % name, "wb", template=fh)
    n = 0

    for line in fh:
        if line.get_tag('rq') <= qvalue:
            continue
        if len(line.seq)<= minlen:
            continue
        if keep=="" or keep=="all":
            pass
        elif gmk2pb(keep) <= n:
            break
        else:
            pass
        fo.write(line)
        n += len(line.seq)

    fh.close()
    fo.close()


def filter_bams(files, qvalue, minlen, keep):

    for file in files:
        filter_bam(file, qvalue, minlen, keep)


def add_hlep_args(parser):

    parser.add_argument('-i', '--input', nargs='+', metavar='FILE', type=str, required=True,
        help='Input reads file, format(bam and sam).')
    parser.add_argument('-q', '--qvalue', metavar='FLOAT', type=float, default=0.8,
        help='Input filtered quality value, default=0.8.')
    parser.add_argument('-l', '--minlen', metavar='FLOAT', type=float, default=500,
        help='Input the minimum read length for filtering, default=500.')
    parser.add_argument('-k', '--keep', metavar='STR', type=str, default='all',
        help='Number of bases reserved, default=all.')

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
    filter_bam.py Filter bam files based on quality values.

attention:
    filter_bam.py -i *.bam
version: %s
contact:  %s <%s>\
        ''' % (__version__, ' '.join(__author__), __email__))

    args = add_hlep_args(parser).parse_args()

    filter_bams(args.input, args.qvalue, args.minlen, args.keep)


if __name__ == "__main__":

    main()
