#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A script for generating contributor lists for astropy.

Note that this requires GitPython (https://gitpython.readthedocs.org).
"""
from __future__ import print_function, division

import os
from git import Repo

def log_repos(repos, logformat, moreargs=None, append_repo_name=False):
    for repodir in repos:
        if not os.path.isdir(repodir):
            raise ValueError('{} is not a directory!'.format(repodir))

    repodct = {}
    for repodir in repos:
        logargs = ["--format=format:{0}".format(logformat)]
        if append_repo_name:
            logargs[0] = logargs[0] + ', repodir=' + repodir
        logargs[0] = logargs[0]+'<END>'
        if moreargs:
            logargs.extend(moreargs)


        repo = Repo(repodir)
        logout = repo.git.log(*logargs)
        if logout.endswith('<END>'):
            logout = logout[:-5]
        repodct[repodir] = logout.split('<END>\n')
    return repodct


def get_long_logs(repos):
    longerlogs = log_repos(repos, "%h, %ad, %aN, %an, %ae", append_repo_name=True)
    outlines = []
    for repo in repos:
        outlines.extend(longerlogs[repo])
    return outlines


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('repos', help='local repositories to search for authors (paths to directories',
                        nargs='+')
    parser.add_argument('-n', '--no-names', action='store_true')
    parser.add_argument('-o', '--output-file', default=None)
    parser.add_argument('-b', '--bullets', action='store_true')
    parser.add_argument('-t', '--html', action='store_true')
    parser.add_argument('-m', '--mailmap-info', action='store_true', help='include a commit history useful for populating the mailmap for the repos.')
    parser.add_argument('-l', '--last-name', action='store_true', help='sort on last name')

    args = parser.parse_args()

    namedct = log_repos(args.repos, '%aN')

    names = []
    for namelist in namedct.values():
        names.extend(namelist)

    unames = set(names)
    if args.last_name:
        unames = sorted(set(names), key=lambda n:n.split()[-1])
    else:
        unames = sorted(set(names))


    outlines = []

    if not args.no_names:
        outlines.append('----NAMES----')
        outlines.extend(unames)

    if args.bullets:
        outlines.append('----BULLETS----')
        for n in unames:
            outlines.append('* '+n)

    if args.html:
        outlines.append('----HTML----')
        for n in unames:
            outlines.append('\t\t\t<li>' + n + '</li>')

    if args.mailmap_info:
        outlines.append('----MAILMAP_COMMIT_LOG----')
        outlines.extend(get_long_logs(args.repos))

    output = '\n'.join(outlines)
    if args.output_file is None:
        print(output)
    else:
        with open(args.output_file, 'w') as f:
            f.write(output)
