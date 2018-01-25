# The purpose of this script is to download information about all pull
# requests merged into the master branch of the given repository. This
# information is downloaded to a JSON file. This includes the 'last
# modified' date for all pull requests, so that when the script is re-run,
# only modified or new entries are downloaded.

import os
import sys
import json

from datetime import datetime, timedelta
try:
    from github3 import GitHub
    from github3.null import NullObject
except ImportError:
    raise ImportError('Please conda or pip install github3.py')

# NOTE: Comment this out if don't need GitHub authentication
from common import get_credentials


def parse_isoformat(string):
    return datetime.strptime(string, "%Y-%m-%dT%H:%M:%S")


if sys.argv[1:]:
    REPOSITORY = sys.argv[1]
else:
    REPOSITORY = 'astropy/astropy'

NAME = os.path.basename(REPOSITORY)

print("The repository this script currently works with is '{}'.\n"
      .format(REPOSITORY))


# Get handle to repository
g = GitHub(*get_credentials())  # NOTE: With authentication
# g = GitHub()  # NOTE: No authentication (has API limit)
repo = g.repository(*REPOSITORY.split('/'))

# We continue from an existing file rather than starting from scratch. To start
# from scratch, just remove the JSON file

json_filename = 'merged_pull_requests_{}.json'.format(NAME)

if os.path.exists(json_filename):
    with open(json_filename) as merged:
        pull_requests = json.load(merged)
else:
    pull_requests = {}

LAST_MODIFIED_DATE = None
for pr in pull_requests.values():
    date = parse_isoformat(pr['updated'])
    if LAST_MODIFIED_DATE is None or date > LAST_MODIFIED_DATE:
        LAST_MODIFIED_DATE = date

# FIXME: at the moment, because we don't store time zones, to be safe we check
# for pull requests modified within 24 hours of the cutoff.
if LAST_MODIFIED_DATE is not None:
    LAST_MODIFIED_DATE -= timedelta(hours=24)
else:
    # With an empty JSON file, we use the date of PR#1
    LAST_MODIFIED_DATE = datetime(2014, 6, 13, 1, 48, 44)

print("Last modified date: {0}".format(LAST_MODIFIED_DATE))

# We enclose the following code in a try...finally so that if the updating
# crashes, we still write out what we had.

try:

    # Find the maximum issue number
    for issue in repo.issues(state='closed', sort='created'):
        max_issues = issue.number
        break

    # repo.get_pulls doesn't seem to get quite all available pull requests
    # because state:closed seems to miss some PRs that appear with is:closed
    # so instead we use get_issues and then get the PR objects manually.
    # This allows us to also only iterate over issues that have been updated
    # since a certain time.
    for i, issue in enumerate(repo.issues(since=LAST_MODIFIED_DATE,
                                          state='closed')):

        pr = issue.pull_request()

        if isinstance(pr, NullObject):
            continue

        if not pr.merged:
            continue

        if pr.base.ref != 'master':
            continue

        if str(pr.number) in pull_requests:
            if (pr.updated_at.replace(tzinfo=None) >
                    parse_isoformat(pull_requests[str(pr.number)]['updated'])):
                print("Updating entry for pull request #{} ({} of "
                      "max {})".format(pr.number, i, max_issues))
            else:
                print("Entry for pull request #{} is "
                      "up to date".format(pr.number, i, max_issues))
        else:
            print("Fetching new entry for pull request "
                  "#{} ({} of max {})".format(pr.number, i, max_issues))

        if pr.milestone is None:
            milestone = None
        else:
            milestone = pr.milestone['title']

        # Get labels
        labels = [label.name for label in issue.labels()]

        pull_requests[str(pr.number)] = {'milestone': milestone,
                                         'title': pr.title,
                                         'labels': labels,
                                         'merged': pr.merged_at.isoformat(),
                                         'updated': pr.updated_at.isoformat(),
                                         'created': pr.created_at.isoformat(),
                                         'merge_commit': pr.merge_commit_sha}

finally:

    with open(json_filename, 'w') as f:
        json.dump(pull_requests, f, sort_keys=True, indent=2)
