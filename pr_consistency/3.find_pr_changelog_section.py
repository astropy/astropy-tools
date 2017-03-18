# The purpose of this script is to search through the latest changelog to find
# for each pull request what section of the changelog the pull request is
# mentioned in. The output is a JSON file that contains for each pull request
# the changelog section.

import os
import re
import sys
import json
import tempfile

import requests

if sys.argv[1:]:
    REPOSITORY = sys.argv[1]
else:
    REPOSITORY = 'astropy/astropy'

NAME = os.path.basename(REPOSITORY)

print("The repository this script currently works with is '{}'.\n"
      .format(REPOSITORY))

CHANGELOG = 'https://raw.githubusercontent.com/{}/master/CHANGES.rst'.format(REPOSITORY)
TMPDIR = tempfile.mkdtemp()

BLOCK_PATTERN = re.compile('\[#.+\]', flags=re.DOTALL)
ISSUE_PATTERN = re.compile('#[0-9]+')


def find_prs_in_changelog(content):
    issue_numbers = []
    for block in BLOCK_PATTERN.finditer(content):
        block_start, block_end = block.start(), block.end()
        block = content[block_start:block_end]
        for m in ISSUE_PATTERN.finditer(block):
            start, end = m.start(), m.end()
            issue_numbers.append(block[start:end][1:])
    return issue_numbers

# Get all the PR numbers from the changelog

changelog_prs = {}
version = None
content = ''
previous = None

for line in requests.get(CHANGELOG).text.splitlines():
    if '-------' in line:
        if version is not None:
            for pr in find_prs_in_changelog(content):
                changelog_prs[pr] = version
        version = previous.strip().split('(')[0].strip()
        if 'v' not in version:
            version = 'v' + version
        content = ''
    elif version is not None:
        content += line
    previous = line

with open('pull_requests_changelog_sections_{}.json'.format(NAME), 'w') as f:
    json.dump(changelog_prs, f, sort_keys=True, indent=2)
