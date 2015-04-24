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


GH_API_BASE_URL = 'https://api.github.com'


def issue_to_pr(issuenum, srcbranch, repo='astropy', targetuser='astropy',
                targetbranch='master', baseurl=GH_API_BASE_URL):
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

    data = {'issue': str(issuenum),
            'head': username + ':' + srcbranch,
            'base': targetbranch}

    datajson = json.dumps(data)

    suburl = 'repos/{user}/{repo}/pulls'.format(user=targetuser, repo=repo)
    url = basejoin(baseurl, suburl)
    res = requests.post(url, data=datajson, auth=get_credentials())
    return res.json()


def get_credentials():
    username = password = None

    try:
        my_netrc = netrc.netrc()
    except:
        pass
    else:
        auth = my_netrc.authenticators(GITHUB_API_HOST)
        if auth:
            response = ''
            while response.lower() not in ('y', 'n'):
                log.info('Using the following GitHub credentials from '
                      '~/.netrc: {0}/{1}'.format(auth[0], '*' * 8))
                response = input(
                    'Use these credentials (if not you will be prompted '
                    'for new credentials)? [Y/n] ')
            if response.lower() == 'y':
                username = auth[0]
                password = auth[2]

    if not (username and password):
        log.info("Enter your GitHub username and password so that API "
                 "requests aren't as severely rate-limited...")
        username = input('Username: ')
        password = getpass.getpass('Password: ')

    return username, password


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
                        default=GH_API_BASE_URL, help='The base '
                        'URL for github (default: %(default)s)')

    args = parser.parse_args(argv)

    targrepo = args.targetuser + '/' + args.repo

    print('Converting issue', args.issuenum, 'of', targrepo, 'to pull request')
    print('Will request to pull branch', args.srcbranch, 'of user\'s',
          args.repo, 'repo to branch', args.targbranch, 'of ', targrepo)
    issue_to_pr(args.issuenum, args.srcbranch, args.repo, args.targetuser,
                args.targbranch, args.baseurl)


if __name__ == '__main__':
    main()
