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
import getpass
import json
import sys
import urllib

try:
    import requests
except ImportError:
    print('This script requests the requests module--it can be installed '
          '`pip install requests`, or your package manager of choice.',
          file=sys.stderr)
    sys.exit(1)


GH_API_BASE_URL = 'https://api.github.com'


def issue_to_pr(issuenum, srcbranch, repo='astropy', targetuser='astropy',
                targetbranch='master', username=None, pw=None,
                baseurl=GH_API_BASE_URL):
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
    username : str or None
        The name of the user sourcing the pull request.  If None, the caller
        will be prompted for their name at the terminal.
    pw : str or None
        The password of the user sourcing the pull request.  If None, the
       caller will be prompted for their name at the terminal (text will be
       hidden).
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

    if username is None:
        username = raw_input('Username: ')
    if pw is None:
        pw = getpass.getpass()

    auth = (username, pw)

    data = {'issue': str(issuenum),
            'head': username + ':' + srcbranch,
            'base': targetbranch}

    datajson = json.dumps(data)

    suburl = 'repos/{user}/{repo}/pulls'.format(user=targetuser, repo=repo)
    url = urllib.basejoin(baseurl, suburl)
    res = requests.post(url, data=datajson, auth=auth)
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
    parser.add_argument('--targetuser', metavar='USER', type=str,
                        default='astropy', help='The name of the '
                        'user/organization the pull request should pull into '
                        '(default: astropy)')
    parser.add_argument('--targbranch', metavar='BRANCH', type=str,
                        default='master', help='The branch name the pull '
                        'request should be pulled into (default: master)')
    parser.add_argument('--baseurl', metavar='URL', type=str,
                        default='https://api.github.com', help='The base '
                        'URL for github (default: https://api.github.com)')

    args = parser.parse_args(argv)

    targrepo = args.targetuser + '/' + args.repo

    print('Converting issue', args.issuenum, 'of', targrepo, 'to pull request')
    print('Will request to pull branch', args.srcbranch, 'of user\'s',
          args.repo, 'repo to branch', args.targbranch, 'of ', targrepo)
    issue_to_pr(args.issuenum, args.srcbranch, args.repo, args.targetuser,
                args.targbranch, None, None, args.baseurl)


if __name__ == '__main__':
    main()
