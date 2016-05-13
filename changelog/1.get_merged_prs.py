import os
import json

from datetime import datetime
from github import Github

from common import get_credentials


def parse_isoformat(string):
    return datetime.strptime(string, "%Y-%m-%dT%H:%M:%S")


g = Github(*get_credentials())

repo = g.get_organization('astropy').get_repo('astropy')

# We continue from an existing file rather than starting from scratch. To start
# from scratch, just remove the JSON file
if os.path.exists('merged_pull_requests.json'):
    with open('merged_pull_requests.json') as merged:
        pull_requests = json.load(merged)
else:
    pull_requests = {}

try:

    for pr in repo.get_pulls(state='closed', sort='updated', direction='desc', base='master'):

        if not pr.merged:
            continue

        if str(pr.number) in pull_requests:
            if pr.updated_at > parse_isoformat(pull_requests[str(pr.number)]['updated']):
                print("Updating entry for pull request #{0}".format(pr.number))
            else:
                break
        else:
            print("Fetching new entry for pull request #{0}".format(pr.number))

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
                                         'updated': pr.updated_at.isoformat()}

finally:

    with open('merged_pull_requests.json', 'w') as f:
        json.dump(pull_requests, f, sort_keys=True, indent=2)
