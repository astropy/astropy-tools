#!/usr/bin/env python
from __future__ import print_function

"""
This script will use PyPI to identify a release of a package, and then search
through github to get a count of all of the issues and PRs closed/merged since
that release.

Usage:
python gh_issuereport.py astropy/astropy astropy/0.3

Note that it will prompt you for yout github username/password.  This isn't
necessary if you have less than 6000 combined issues/PRs, but if you have more
than that (or run the script multiple times in an hour without caching), you
might hit github's 60 api calls per hour limit (which increases to 5000 if you
log in).

Also note that running this will by default cache the PRs/issues in "prs.json"
and "issues.json".  Give it the "-n" option to not do that.

Requires the requests package (https://pypi.python.org/pypi/requests/).

"""

import argparse
import os
import json
import datetime

from common import get_credentials

import requests
from six import moves

GH_API_BASE_URL = 'https://api.github.com'
ISO_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def paginate_list_request(req, verbose=False, auth=None):
    elems = []
    currreq = req
    i = 1

    while 'next' in currreq.links:
        elems.extend(currreq.json())

        i += 1
        if verbose:
            print('Doing request', i, 'of', currreq.links['last']['url'].split('page=')[-1])
        currreq = requests.get(currreq.links['next']['url'], auth=auth)

    elems.extend(currreq.json())
    return elems


def count_issues_since(dt, repo, auth=None, verbose=True, cacheto=None):
    if cacheto and os.path.exists(cacheto):
        with open(cacheto) as f:
            isslst = json.load(f)
    else:
        url = GH_API_BASE_URL + '/repos/' + repo + '/issues?per_page=100&state=all'

        req = requests.get(url, auth=auth)
        if not req.ok:
            msg = 'Failed to access github API for repo using url {}. {}: {}: {}'
            raise requests.HTTPError(msg.format(url, req.status_code, req.reason, req.text))
        isslst = paginate_list_request(req, verbose, auth=auth)
        if cacheto:
            with open(cacheto, 'w') as f:
                json.dump(isslst, f)

    nopened = nclosed = 0

    for entry in isslst:
        createddt = datetime.datetime.strptime(entry['created_at'],  ISO_FORMAT)
        if createddt > dt:
            nopened += 1

        if entry['closed_at']:
            closeddt = datetime.datetime.strptime(entry['closed_at'],  ISO_FORMAT)
            if closeddt > dt:
                nclosed += 1

    return {'opened': nopened, 'closed': nclosed}


def count_prs_since(dt, repo, auth=None, verbose=True, cacheto=None):
    if cacheto and os.path.exists(cacheto):
        with open(cacheto) as f:
            prlst = json.load(f)
    else:
        url = GH_API_BASE_URL + '/repos/' + repo + '/pulls?per_page=100&state=all'

        req = requests.get(url, auth=auth)
        prlst = paginate_list_request(req, verbose, auth=auth)
        if cacheto:
            with open(cacheto, 'w') as f:
                json.dump(prlst, f)


    nopened = nclosed = 0

    usersopened = []
    usersclosed = []

    for entry in prlst:
        createddt = datetime.datetime.strptime(entry['created_at'],  ISO_FORMAT)
        if createddt > dt:
            nopened += 1
            user = entry['user']
            if user is not None:
                usersopened.append(user['id'])

        if entry['merged_at']:
            closeddt = datetime.datetime.strptime(entry['merged_at'],  ISO_FORMAT)
            if closeddt > dt:
                nclosed += 1
                user = entry['user']
                if user is not None:
                    usersclosed.append(user['id'])

    return {'opened': nopened, 'merged': nclosed,
            'usersopened': len(set(usersopened)),
            'usersmerged': len(set(usersclosed))}


def get_datetime_of_pypi_version(pkg, version):
    resp = requests.get(f"https://pypi.org/pypi/{pkg}/json")
    j = resp.json()

    datestr = j['releases'][version][0]['upload_time']

    return datetime.datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%S")


def main(argv=None):
    parser = argparse.ArgumentParser(description='Print out issue stats since a particular version of a repo.')
    parser.add_argument('repo', help='the github repo to use', metavar='<ghuser>/<reponame>')
    parser.add_argument('package', help='the package/version to lookup on pypi '
                                        'or "None" to skip the lookup',
                                   metavar='<package>/<version>')

    parser.add_argument('-q', '--quiet', help='hide informational messages',
                                         dest='verbose', action='store_false')
    parser.add_argument('-n', '--no-cache', help="don't cache the downloaded "
                                                 "issue/PR info (and don't read "
                                                 "the cached versions)",
                                            dest='cache', action='store_false')

    args = parser.parse_args(argv)
    if args.package.lower() == 'none':
        # probably nothing on github was created before the year 1900...
        pkgdt = datetime.datetime(1900, 1, 1)
        if args.verbose:
            print('Not looking up a PyPI package')
    else:
        pkgdt = get_datetime_of_pypi_version(*args.package.split('/'))
        if args.verbose:
            print('Found PyPI entry for', args.package, ':', pkgdt)

    auth = get_credentials()

    if args.cache:
        icache = 'issues.json'
        prcache = 'prs.json'
    else:
        icache = prcache = None

    if args.verbose:
        print('Counting issues')
    icnt = count_issues_since(pkgdt, args.repo, auth=auth, verbose=args.verbose, cacheto=icache)
    if args.verbose:
        print('Counting PRs')
    prcnt = count_prs_since(pkgdt, args.repo, auth=auth, verbose=args.verbose, cacheto=prcache)

    print(icnt['opened'], 'issues opened since', args.package, 'and', icnt['closed'], 'issues closed')
    print(prcnt['opened'], 'PRs opened since', args.package, 'and', prcnt['merged'], 'PRs merged')
    print(prcnt['usersopened'], 'unique users opened PRs, and', prcnt['usersmerged'], 'of them got it merged')


if __name__ == '__main__':
    main()
