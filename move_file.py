#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import logging
import argparse


LOG = logging.getLogger(__name__)

__version__ = "1.2.0"
__author__ = ("Xingguo Zhang",)
__email__ = "113178210@qq.com"
__all__ = []


def move_file(file, nfile):

    LOG.debug("mv %s %s" % (file, nfile))

    shutil.move(file, nfile)

    return 0


def check_path(path):

    path = os.path.abspath(path)

    if not os.path.exists(path):
        msg = "File not found '{path}'".format(**locals())
        LOG.error(msg)
        raise Exception(msg)

    return path


def move_files(files, path, prefix):

    for file in files:
        line = file.strip().split('/')
        name = line[-1]
        oldp = name.split('.')[0]
        name = name.replace(oldp, prefix)

        if  not path:
            paths = '/'.join(line[0:-1])
        else:
            paths = path
            
        paths = check_path(paths)
        nfile = os.path.join(paths, name)

        move_file(file, nfile)

    return 0


def add_hlep_args(parser):

    parser.add_argument("-f", "--files", nargs='+', metavar='FILE', type=str, required=True,
        help="Input files.")
    parser.add_argument("--path", metavar='FILE', type=str, default='',
        help="The path where the input file needs to be moved.")
    parser.add_argument("-p", "--prefix", metavar='STR', type=str, default='out',
        help="The name of the output file")

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
    move_file.py  Move files

attention:
    move_file.py --files * --prefix name
version: %s
contact:  %s <%s>\
        ''' % (__version__, ' '.join(__author__), __email__))

    args = add_hlep_args(parser).parse_args()

    move_files(args.files, args.path, args.prefix)


if __name__ == "__main__":

    main()
