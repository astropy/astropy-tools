"""
This module has functions to generate various information plots that can be
exctracted from a git repository like how the number of commits and committers
grow over time.

Requires that you have a file that can be generatedwith:
git log --numstat --use-mailmap --format=format:"COMMIT,%H,%at,%aN"
"""

import os
import numpy as np
from matplotlib import pyplot as plt

def generate_commit_stats_file(fn='gitlogstats', overwrite=False):
    """
    Running this will generate a file in the current directory that stores the
    statistics to make generating lots of plots easier.  Delete the file or
    set `overwrite` to True to always re-generate the statistics.
    """
    if os.path.isfile(fn):
        with open(fn) as f:
            return f.read()
    else:
        import subprocess

        cmd = 'git log --numstat --use-mailmap --format=format:"COMMIT,%H,%at,%aN"'.split()
        output = subprocess.check_output(cmd)
        with open(fn, 'w') as f:
            f.write(output)
        return output


def parse_git_log(fn='gitlogstats', recentfirst=False, cumlines=False):
    """
    Returns (authors, datetimes, deltalines) arrays
    """
    from datetime import datetime

    authors = []
    deltalines = []
    datetimes = []

    commitstrs = generate_commit_stats_file(fn).split('COMMIT,')[1:]

    for cs in commitstrs:
        lns = cs.strip().split('\n')
        chash, timestamp, author = lns.pop(0).split(',')
        timestamp = int(timestamp)

        authors.append(author)
        datetimes.append(datetime.utcfromtimestamp(timestamp))

        dellns = 0
        for l in lns:
            add, sub, filename = l.split('\t')
            dellns += int(add.replace('-', '0')) - int(sub.replace('-', '0'))
        deltalines.append(dellns)

    authors, datetimes, deltalines = [np.array(l) for l in (authors, datetimes, deltalines)]

    sorti = np.argsort(datetimes)
    revsorti = np.argsort(sorti)

    if cumlines:
        deltalines = np.cumsum(deltalines[sorti])[revsorti]

    if recentfirst:
        sorti = sorti[::-1]

    return tuple([a[sorti] for a in (authors, datetimes, deltalines)])


def loc_plot():
    from datetime import datetime

    authors, datetimes, nlines = parse_git_log(cumlines=True, recentfirst=False)

    plt.plot(datetimes, nlines, lw=2)

    yrlabels = [2011, 2012, 2013, 2014]

    plt.xticks([datetime(yr, 1, 1) for yr in yrlabels], yrlabels, fontsize=20)
    plt.ylabel('Lines of Code', fontsize=30)

    plt.tight_layout()


def commits_plot():
    from datetime import datetime

    authors, datetimes, deltalines = parse_git_log(recentfirst=False)

    plt.plot(datetimes, np.arange(len(datetimes)) + 1, lw=2)

    yrlabels = [2011, 2012, 2013, 2014]

    plt.xticks([datetime(yr, 1, 1) for yr in yrlabels], yrlabels, fontsize=20)
    plt.ylabel('Number of Commits', fontsize=30)

    plt.tight_layout()


def get_first_commit_map():
    authors, datetimes, deltalines = parse_git_log(recentfirst=False)

    firstcommit = {}
    for au, t in zip(authors, datetimes):
        if au not in firstcommit or firstcommit[au] > t:
            firstcommit[au] = t

    return firstcommit


def commiters_plot():
    from datetime import datetime

    firstcommit = get_first_commit_map()

    dts = np.sort(firstcommit.values())

    plt.plot(dts, np.arange(len(dts)) + 1, lw=2)

    yrlabels = [2011, 2012, 2013, 2014]

    plt.xticks([datetime(yr, 1, 1) for yr in yrlabels], yrlabels, fontsize=20)
    plt.ylabel('# of Code Contributors', fontsize=30)

    plt.tight_layout()
