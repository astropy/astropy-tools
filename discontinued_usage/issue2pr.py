#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Requires python >=2.6
"""
Tool to convert github issues to pull requests by attaching code. Uses the
github v3 API. Defaults assumed for the `astropy <http://www.astropy.org>`_
project.
"""

from __future__ import print_function

import argparse
import json
import sys

from common import get_credentials

try:
    import requests
except ImportError:
    print('This script requests the requests module--it can be installed '
          '`pip install requests`, or your package manager of choice.',
          file=sys.stderr)
    sys.exit(1)


if sys.version_info[0] >= 3:
    # Define raw_input on Python 3
    raw_input = input
    from urllib.parse import urljoin as basejoin
else:
    from urllib import basejoin


GITHUB_API_HOST = 'api.github.com'
GITHUB_API_BASE_URL = 'https://{0}/repos/'.format(GITHUB_API_HOST)


def issue_to_pr(issuenum, srcbranch, repo='astropy', sourceuser='',
                targetuser='astropy', targetbranch='master',
                baseurl=GITHUB_API_BASE_URL):
    """
    Attaches code to an issue, converting a regular issue into a pull request.

    Parameters
    ----------
    issuenum : int
        The issue number (in `targetuser`/`repo`) onto which the code should be
        attached.
    srcbranch : str
        The branch (in `username`/`repo`) the from which to attach the code.
        After this is complete, further updates to this branch will be passed
        on to the pull request.
    repo : str
        The name of the repository (the same-name repo should be present for
        both `targetuser` and `username`).
    targetuser : str
        The name of the user/organization that has the issue.
    targetbranch : str
        The name of the branch (in `targetuser`/`repo`) that the pull request
        should merge into.
   baseurl : str
       The URL to use to access the github site (including protocol).

    .. warning::
        Be cautious supplying `pw` as a string - if you do this in an ipython
        session, for example, it will be logged in the input history, revealing
        your password in clear text.  When in doubt, leave it as `None`,
        as this will securely prompt you for your password.

    Returns
    -------
    response : str
        The json-decoded response from the github server.
    error message : str, optional
        If present, indicates github responded with an HTTP error.

    """

    while not sourceuser:
        sourceuser = raw_input('Enter GitHub username to create pull request '
                               'from: ').strip()

    username, password = get_credentials(username=sourceuser)

    data = {'issue': str(issuenum),
            'head': sourceuser + ':' + srcbranch,
            'base': targetbranch}

    datajson = json.dumps(data)

    suburl = '{user}/{repo}/pulls'.format(user=targetuser, repo=repo)
    url = basejoin(baseurl, suburl)
    res = requests.post(url, data=datajson, auth=(username, password))
    return res.json()


def main(argv=None):
    if sys.version_info < (2,6):
        print('issue2pr.py requires Python >=2.6, exiting')
        sys.exit(-1)

    descr = 'Convert a github issue to a Pull Request by attaching code.'
    parser = argparse.ArgumentParser(description=descr)

    parser.add_argument('srcbranch', metavar='BRANCH', type=str, help='The '
                        'name of the branch in the source (user\'s) repository '
                        'that is to be pulled into the target.')
    parser.add_argument('issuenum', metavar='ISSUE', type=int,
                        help='The issue number from the target repository')
    parser.add_argument('--repo', metavar='REPO', type=str,
                        default='astropy', help='The name of the repository '
                        'of the issue and code. must have the same name for '
                        'both target and source (default: astropy)')
    parser.add_argument('--sourceuser', metavar='USER', type=str,
                        help='The name of the user/organization whose '
                             'repo/fork the pull request should pull from')
    parser.add_argument('--targetuser', metavar='USER', type=str,
                        default='astropy', help='The name of the '
                        'user/organization the pull request should pull into '
                        '(default: astropy)')
    parser.add_argument('--targbranch', metavar='BRANCH', type=str,
                        default='master', help='The branch name the pull '
                        'request should be pulled into (default: master)')
    parser.add_argument('--baseurl', metavar='URL', type=str,
                        default=GITHUB_API_BASE_URL, help='The base '
                        'URL for github (default: %(default)s)')

    args = parser.parse_args(argv)

    targrepo = args.targetuser + '/' + args.repo

    print('Converting issue', args.issuenum, 'of', targrepo, 'to pull request')
    print('Will request to pull branch', args.srcbranch, 'of user\'s',
          args.repo, 'repo to branch', args.targbranch, 'of ', targrepo)
    issue_to_pr(args.issuenum, args.srcbranch, args.repo, args.sourceuser,
                args.targetuser, args.targbranch, args.baseurl)


if __name__ == '__main__':
    main()
