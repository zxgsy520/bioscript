#!/usr/bin/env python
#coding:utf-8

import os
import re
import sys
import pysam
import shutil
import logging
import argparse


LOG = logging.getLogger(__name__)

__version__ = "1.0.0"
__author__ = ("Xingguo Zhang",)
__email__ = "113178210@qq.com"
__all__ = []


def check_path(path):

    path = os.path.abspath(path)

    if not os.path.exists(path):
        msg = "File not found '{path}'".format(**locals())
        LOG.error(msg)
        raise Exception(msg)

    return path


def link(source, target, force=False):
    """
    link -s
    :param source:
    :param target:
    :param force:
    :return:
    """
    source = check_path(source)

    # for link -sf
    if os.path.exists(target):
        if force:
            os.remove(target)
        else:
            raise Exception("%r has been exist" % target)

    LOG.info("ln -s {source} {target}".format(**locals()))
    os.symlink(source, target)

    return os.path.abspath(target)


def copy(source, target, force=False):

    source = check_path(source)

    if os.path.exists(target):
        if force:
            os.remove(target)
        else:
            raise Exception("%r has been exist" % target)

    LOG.info("cp {source} {target}".format(**locals()))

    shutil.copy(source, target)

    return os.path.abspath(target)


def move(source, target, force=False):

    source = check_path(source)

    if os.path.exists(target):
        if force:
            os.remove(target)
        else:
            raise Exception("%r has been exist" % target)

    LOG.info("mv {source} {target}".format(**locals()))

    shutil.move(source, target)

    return os.path.abspath(target)


def get_sample(file):

    name = file.split('/')[-1]

    if '--' in name:
        name = name.split('--')[1].split('.bam')[0]
    else:
        name = name.split('.')[0]

    return name


def sort_file(files):

    data = {}

    for file in files:
        name = get_sample(file)

        if name not in data:
            data[name] = []
        data[name].append(file)

    return data


def merge_bam(source, target):

    fo = ''

    for file in source:
        file = check_path(file)
        fh = pysam.AlignmentFile(file, "rb", check_sq=False)

        if fo == '':
            fo = pysam.AlignmentFile(target, "wb", template=fh)

        for line in fh:
            fo.write(line)
        fh.close()
    fo.close()


def run_merge_bam(files):

    data = sort_file(files)

    for name in data:
        target = '%s.bam' % name
        source = data[name]

        if len(source)==1:
            target = copy(source[0], target, force=False)
            print('merge %s:%s\t%s' % (name, source[0], target))
        elif len(source)>1:
            target = merge_bam(source, target)
            print('merge %s:%s\t%s' % (name, ','.join(source), target))
        else:
            raise Exception("The file path of sample %s does not exist" % name)

    return 0


def add_hlep_args(parser):

    parser.add_argument('-i', '--input', nargs='+', metavar='FILE', type=str, required=True,
        help='Input reads file, format(bam and sam).')

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
    merge_bam.py Merge bam

attention:
    merge_bam.py -i *.bam
version: %s
contact:  %s <%s>\
        ''' % (__version__, ' '.join(__author__), __email__))

    args = add_hlep_args(parser).parse_args()

    run_merge_bam(args.input)


if __name__ == "__main__":

    main()
