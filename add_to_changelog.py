#!/usr/bin/env python
from __future__ import print_function

import re
import argparse


NEW_CHANGELOG_TEMPLATE = """{newvers} (unreleased)
{newvers_head}-------------

New Features
^^^^^^^^^^^^

{package_list}

API Changes
^^^^^^^^^^^

{package_list}

Bug Fixes
^^^^^^^^^

{package_list}

Other Changes and Additions
^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Nothing changed yet.

"""


new_version_re = re.compile(r'--*$')
package_re = re.compile(r'- ``(astropy\..*)``$')

def find_all_package_sections(fn):
    pkg_list = []

    firstvers = False
    with open(fn) as f:
        for l in f:
            if new_version_re.match(l):
                # this lets us go through exactly one version
                if firstvers:
                    break
                else:
                    firstvers = True

            m = package_re.match(l)
            if m:
                pnm = m.group(1)
                if pnm not in pkg_list:
                    pkg_list.append(pnm)

    return pkg_list


def main(argv=None):
    parser = argparse.ArgumentParser(description='Print out the')
    parser.add_argument('changelog', help='path to the changelog to use as a '
                                          'template')
    parser.add_argument('version', help='the new version to generate the '
                                        'changelog for')

    args = parser.parse_args(argv)

    pkg_list = find_all_package_sections(args.changelog)

    pkg_list_str = '\n\n'.join(['- ``{}``'.format(pnm) for pnm in pkg_list])


    new_changelog = NEW_CHANGELOG_TEMPLATE.format(newvers=args.version,
                                                  newvers_head='-'*len(args.version),
                                                  package_list=pkg_list_str)
    print(new_changelog)

if __name__ == '__main__':
    main()
