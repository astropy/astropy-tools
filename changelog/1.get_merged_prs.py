# The purpose of this script is to download information about all pull requests
# merged into the master branch of the astropy repository. This information is
# downloaded to a JSON file. This includes the 'last modified' date for all pull
# requests, so that when the script is re-run, only modified or new entries are
# downloaded. At this time, this script requires the developer version of the
# pygithub package.

import os
import json

from datetime import datetime
from github import Github

from common import get_credentials


def parse_isoformat(string):
    return datetime.strptime(string, "%Y-%m-%dT%H:%M:%S")

REPOSITORY = 'astropy/astropy'

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

# We enclose the following code in a try...finally so that if the updating
# crashes, we still write out what we had.

try:
    max_issues = repo.get_issues(state='all',sort='created')[0].number
    i = 0
    for pr in repo.get_pulls(state='closed', sort='updated', direction='desc', base='master'):
        i += 1
        if not pr.merged:
            continue

        if str(pr.number) in pull_requests:
            if pr.updated_at > parse_isoformat(pull_requests[str(pr.number)]['updated']):
                print("Updating entry for pull request #{} ({} of max {})".format(pr.number, i, max_issues))
            else:
                break
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
