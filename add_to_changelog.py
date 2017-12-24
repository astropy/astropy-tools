#!/usr/bin/env python
from __future__ import print_function

"""
A script to generate a changelog section for a new version of astropy.
Use like:

$ python add_to_changelog.py ../astropy/CHANGES.rst v1.2

And it will print out a new changelog section for v1.2.

Note that this uses the CHANGES.rst that's the first argument to figure out what
all the sections are that should go in the new changelog.  So be sure it points
to a CHANGES.rst that's up-to-date with all the sections the new version should
have.
"""

import re
import argparse


NEW_CHANGELOG_TEMPLATE = """{newvers} (unreleased)
{newvers_head}=============

New Features
------------

{package_list}

API Changes
-----------

{package_list}

Bug Fixes
---------

{package_list}

Other Changes and Additions
---------------------------

- Nothing changed yet.

"""


new_version_re = re.compile(r'==*$')
package_re = re.compile(r'(astropy\..*)$')

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
    parser = argparse.ArgumentParser(description='Print out the changelog for '
                                                 'a new version of Astropy.')
    parser.add_argument('changelog', help='path to the changelog to use as a '
                                          'template')
    parser.add_argument('version', help='the new version to generate the '
                                        'changelog for')
    parser.add_argument('--write', '-w', action='store_true', help='update the '
                                         'referenced changelog (the first '
                                         'argument) to include the generated '
                                         'changelog at the top (or if -l is '
                                         'set, it determines the location).')
    parser.add_argument('--last-version', '-l', help='The name of the version '
                       'that this changelog entry should precede.  If not '
                       'given, this changelog will go at the top', default='')

    args = parser.parse_args(argv)

    pkg_list = find_all_package_sections(args.changelog)

    pkg_list_str = '\n\n'.join(['{}\n{}'.format(pnm, '^'*len(pnm)) for pnm in pkg_list])


    new_changelog = NEW_CHANGELOG_TEMPLATE.format(newvers=args.version,
                                                  newvers_head='='*len(args.version),
                                                  package_list=pkg_list_str)
    if args.write:
        with open(args.changelog) as fr:
            old_changelog = fr.read()
        with open(args.changelog, 'w') as fw:
            if args.last_version:
                header_match = None
                for l in old_changelog.split('\n'):
                    if args.last_version + ' (' in l:
                        header_match = l + '\n'
                    elif header_match:
                        if '='*len(args.last_version) in l:
                            fw.write('\n\n')
                            fw.write(new_changelog)
                            fw.write('\n\n\n')
                        fw.write(header_match)
                        fw.write(l)
                        fw.write('\n')
                        header_match = None
                    else:
                        fw.write(l)
                        fw.write('\n')
            else:
                fw.write(new_changelog)
                fw.write('\n\n\n')
                fw.write(old_changelog)

    print(new_changelog)

if __name__ == '__main__':
    main()
