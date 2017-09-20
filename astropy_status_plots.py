"""
This module has functions to generate various information plots that can be
extracted from a git repository like how the number of commits and committers
grow over time.

Requires that you have a file that can be generatedwith:
git log --numstat --use-mailmap --format=format:"COMMIT,%H,%at,%aN"
"""

import os
import numpy as np
from matplotlib import pyplot as plt

def generate_commit_stats_file(fn='gitlogstats', overwrite=False, dirtorunin=None):
    """
    Running this will generate a file in the current directory that stores the
    statistics to make generating lots of plots easier.  Delete the file or
    set `overwrite` to True to always re-generate the statistics.
    """
    if os.path.isfile(fn) and not overwrite:
        with open(fn) as f:
            return f.read()
    else:
        import subprocess

        cmd = 'git log --numstat --use-mailmap --format=format:"COMMIT,%H,%at,%aN"'.split()
        output = subprocess.check_output(cmd, cwd=dirtorunin)
        with open(fn, 'wb') as f:
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
            if len(l.split('\t')) != 3:
                #print('skipping "{0}"'.format(l))
                continue
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


def loc_plot(yrlabels=None):
    from datetime import datetime

    authors, datetimes, nlines = parse_git_log(cumlines=True, recentfirst=False)

    plt.plot(datetimes, nlines, lw=2)

    if yrlabels is None:
        yrlabels = np.arange((datetime.today().year - 2011) + 1) + 2011

    plt.xticks([datetime(yr, 1, 1) for yr in yrlabels], yrlabels, fontsize=20)
    plt.ylabel('Lines of Code', fontsize=30)

    plt.tight_layout()


def commits_plot(yrlabels=None, **plotkws):
    from datetime import datetime

    authors, datetimes, deltalines = parse_git_log(recentfirst=False)

    plotkws.setdefault('lw', 2)
    plt.plot(datetimes, np.arange(len(datetimes)) + 1, **plotkws)

    if yrlabels is None:
        yrlabels = np.arange((datetime.today().year - 2011) + 1) + 2011


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


def commiters_plot(yrlabels=None, **plotkws):
    from datetime import datetime

    firstcommit = get_first_commit_map()

    dts = np.sort(list(firstcommit.values()))

    plotkws.setdefault('lw', 2)
    plt.plot(dts, np.arange(len(dts)) + 1, **plotkws)

    if yrlabels is None:
        yrlabels = np.arange((datetime.today().year - 2011) + 1) + 2011

    plt.xticks([datetime(yr, 1, 1) for yr in yrlabels], yrlabels, fontsize=20)

    plt.ylim(0, len(dts)+1)
    plt.xlim(dts[0], dts[-1])

    ytks = [y for y in plt.yticks()[0] if y<plt.ylim()[-1]]
    if len(dts)+1 not in ytks:
        ytks.append(len(dts)+1)
    plt.yticks(ytks, fontsize=20)

    plt.ylabel('# of Code Contributors', fontsize=30)
    plt.tight_layout()

    return len(dts)+1

def get_paper_citations(paperbibcode='2013A&A...558A..33A', apikey=None, fields='bibcode,pubdate'):
    """
    Gets the citations for the requested paper using the ADS API.  Requires an
    ADS API key, or an ``adsapikey`` file locally

    Requires that the `requests` package be installed
    """
    import requests

    if apikey is None:
        apikeyfn = 'adsapikey'
        if os.path.exists(apikeyfn):
            with open(apikeyfn, 'r') as f:
                apikey = f.read().strip()
        else:
            raise ValueError('No ADS API key given and no adsapikey file found')

    headers = {'Authorization': 'Bearer:' + apikey}
    get_ads = lambda apiend, params=None: requests.get('http://api.adsabs.harvard.edu/v1/'+apiend, params=params, headers=headers)

    params = {'q': 'citations(bibcode:{0})'.format(paperbibcode),
              'fl': fields,
              'rows': '10000'}

    resp = get_ads('search/query', params)
    j = resp.json()['response']

    doclists = {n:[] for n in fields.split(',')}

    for doc in j['docs']:
        for n in doclists:
            doclists[n].append(doc[n])
    return doclists

def plot_paper_citations(paperbibcode=None, **plotkws):
    from astropy.time import Time
    from matplotlib.dates import YearLocator, MonthLocator, DateFormatter


    if paperbibcode is None:
        citations = get_paper_citations()
    else:
        citations = get_paper_citations(paperbibcode)

    datenums = np.sort([Time(date.replace('-00','-01')).plot_date for date in citations['pubdate']])

    fig = plt.gcf()
    ax = plt.gca()

    plotkws.setdefault('lw', 2)
    plotkws.setdefault('ls', '-')
    plotkws.setdefault('ms', 0)
    ax.plot_date(datenums, np.arange(len(datenums)), **plotkws)


    ax.xaxis.set_major_locator(YearLocator())
    ax.xaxis.set_major_formatter(DateFormatter('%Y'))
    ax.xaxis.set_minor_locator(MonthLocator())
    ax.autoscale_view()

    fig.autofmt_xdate()

    plt.ylabel('# of Citations', fontsize=30)
    plt.xticks(fontsize=20)
    plt.tight_layout()

    return datenums

def plot_docs_visits(analyics_csvfn, **plotkws):
    """
    Requires a CSV file downloaded from the astropy google analytics page.
    Should have at least the "all sessions" and "Docs visits" segments exported
    from Apr 1 2012 (~when data taking started) to now.
    """
    from datetime import datetime
    from astropy.table import Table
    from astropy.time import Time
    from matplotlib.dates import YearLocator, MonthLocator, DateFormatter

    #first read the data
    tab = Table.read(analyics_csvfn, format='csv',data_start=6, header_start=5)

    # now extract the data

    if tab.colnames[0] == 'Day Index':
        #it's just days, so parse them as such
        times = []
        time_msk = []
        for day, masked in zip(tab['Day Index'], tab['Day Index'].mask):
            if masked:
                times.append(datetime(2000, 1, 1))  #prior to astropy
                time_msk.append(False)
            else:
                times.append(datetime.strptime(day,  '%m/%d/%y'))
                time_msk.append(True)

        times = Time(times)
        # remove the final day because it might be incomplete
        time_msk = np.array(time_msk)&(times!=np.max(times))

    else:  # it's something more complex with an inex and a range
        index = tab[tab.colnames[0]]  # might be called "week index" or "day index" or whatever

        date_range = tab['Date Range'][0]
        if not np.all(date_range== tab['Date Range']):
            raise ValueError('Do not know how to deal with multiple date ranges...')

        t1, t2 = [Time(datetime.strptime(dr, '%b %d, %Y')) for dr in date_range.split(' - ')]
        dti = (t2 - t1)/np.max(index)
        times = t1 + index.view(np.ndarray)*dti

        # remove the final index because it might be incomplete
        time_msk = (index != np.max(index))&~index.mask

    all_msk = (tab['Segment']=='All Sessions') & time_msk
    docs_msk = (tab['Segment']=='Docs Visits') & time_msk

    n_docs = [float(numstr.replace(',', '')) for numstr in tab['Sessions'][docs_msk]]
    times_docs = times[docs_msk]
    n_all= [float(numstr.replace(',', '')) for numstr in tab['Sessions'][all_msk]]
    times_all = times[all_msk]

    #now plot
    fig = plt.gcf()
    ax = plt.gca()

    plotkws.setdefault('lw', 2)
    plotkws.setdefault('ls', '-')
    plotkws.setdefault('ms', 0)
    ax.plot_date(times_docs.plot_date, n_docs, **plotkws)

    ax.xaxis.set_major_locator(YearLocator())
    ax.xaxis.set_major_formatter(DateFormatter('%Y'))
    ax.xaxis.set_minor_locator(MonthLocator())
    ax.autoscale_view()

    fig.autofmt_xdate()

    plt.ylabel('Docs Visits', fontsize=30)
    plt.xticks(fontsize=20)
    plt.tight_layout()

    return (times_docs, n_docs), (times_all, n_all)

