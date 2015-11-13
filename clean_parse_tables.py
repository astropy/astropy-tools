#!/usr/bin/env python

"""
A utility to fix PLY-generated lex and yacc tables to be Python 2 and
3 compatible.
"""
from __future__ import print_function

import os
import argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('dir', help='The directory to search through for lextab/parsetab files.')
args = parser.parse_args()

for root, dirs, files in os.walk(args.dir):
    for fname in files:
        if not (fname.endswith('lextab.py') or fname.endswith('parsetab.py')):
            continue

        path = os.path.join(root, fname)
        print('Found file', path, 'to fix')
        with open(path, 'rb') as fd:
            lines = fd.readlines()

        with open(path, 'wb') as fd:
            if not lines[0].startswith("# Licensed under a 3-clause BSD style license - see LICENSE.rst"):
                print('Re-writing license')
                fd.write("# Licensed under a 3-clause BSD style license - see LICENSE.rst\n")
                fd.write("from __future__ import (absolute_import, division, print_function, unicode_literals)\n")
                fd.write('\n')

            lines = [x.replace("u'", "'").replace('u"', '"') for x in lines]
            lines = [x for x in lines if not (fname in x and x[0] == '#')]

            fd.write(''.join(lines))
