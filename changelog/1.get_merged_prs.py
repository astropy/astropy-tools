# The purpose of this script is to download information about all pull requests
# merged into the master branch of the astropy repository. This information is
# downloaded to a JSON file. This includes the 'last modified' date for all pull
# requests, so that when the script is re-run, only modified or new entries are
# downloaded. At this time, this script requires the developer version of the
# pygithub package.

import os
import json

from datetime import datetime, timedelta
from github import Github

from common import get_credentials


def parse_isoformat(string):
    return datetime.strptime(string, "%Y-%m-%dT%H:%M:%S")

REPOSITORY = 'astropy/astropy'

YESTERDAY = datetime(2016, 12, 13, 0, 0, 0)

# Get handle to repository
g = Github(*get_credentials())
repo = g.get_repo(REPOSITORY)

# We continue from an existing file rather than starting from scratch. To start
# from scratch, just remove the JSON file
if os.path.exists('merged_pull_requests.json'):
    with open('merged_pull_requests.json') as merged:
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

print("Last modified date: {0}".format(LAST_MODIFIED_DATE))

# We enclose the following code in a try...finally so that if the updating
# crashes, we still write out what we had.

try:

    # Find the maximum issue number
    max_issues = repo.get_issues(state='closed', sort='created')[0].number

    # repo.get_pulls doesn't seem to get quite all available pull requests
    # because state:closed seems to miss some PRs that appear with is:closed
    # so instead we use get_issues and then get the PR objects manually.
    # This allows us to also only iterate over issues that have been updated
    # since a certain time.
    for i, issue in enumerate(repo.get_issues(since=LAST_MODIFIED_DATE, state='closed')):

        if issue.pull_request is None:
            continue

        pr = repo.get_pull(issue.number)

        if not pr.merged:
            continue

        if pr.base.ref != 'master':
            continue

        if str(pr.number) in pull_requests:
            if pr.updated_at > parse_isoformat(pull_requests[str(pr.number)]['updated']):
                print("Updating entry for pull request #{} ({} of max {})".format(pr.number, i, max_issues))
            else:
                print("Entry for pull request #{} is up to date".format(pr.number, i, max_issues))
        else:
            print("Fetching new entry for pull request #{} ({} of max {})".format(pr.number, i, max_issues))

        if pr.milestone is None:
            milestone = None
        else:
            milestone = pr.milestone.title

        # Get labels
        issue = repo.get_issue(pr.number)
        labels = [label.name for label in issue.labels]

        pull_requests[str(pr.number)] = {'milestone': milestone,
                                         'title': pr.title,
                                         'labels': labels,
                                         'merged': pr.merged_at.isoformat(),
                                         'updated': pr.updated_at.isoformat(),
                                         'created': pr.created_at.isoformat(),
                                         'merge_commit': pr.merge_commit_sha}

finally:

    with open('merged_pull_requests.json', 'w') as f:
        json.dump(pull_requests, f, sort_keys=True, indent=2)
