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

if sys.argv[2:]:
    CHANGELOG_NAME = sys.argv[2]
else:
    CHANGELOG_NAME = 'CHANGES.rst'

NAME = os.path.basename(REPOSITORY)

print("The repository this script currently works with is '{}'.\n"
      .format(REPOSITORY))

if os.environ.get('LOCAL_CHANGELOG'):
    CHANGELOG = os.environ['LOCAL_CHANGELOG']
    with open(CHANGELOG) as f:
        changelog_lines = f.readlines()
else:
    CHANGELOG = f'https://raw.githubusercontent.com/{REPOSITORY}/master/{CHANGELOG_NAME}'
    changelog_lines = requests.get(CHANGELOG).text.splitlines()

TMPDIR = tempfile.mkdtemp()

BLOCK_PATTERN = re.compile(r'[\[(]#[0-9#, ]+[\])]')
ISSUE_PATTERN = re.compile(r'#[0-9]+')


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

new_changelog_format = False

for line in changelog_lines:
    if '=======' in line:
        new_changelog_format = True
    if '=======' in line or (not new_changelog_format and '-------' in line):
        if version is not None:
            for pr in find_prs_in_changelog(content):
                changelog_prs[pr] = version
        version = previous.strip().split('(')[0].strip()
        if version.startswith('Version '):
            version = version.split()[1]
        if 'v' not in version:
            version = 'v' + version
        content = ''

    elif version is not None:
        content += line
    previous = line

with open(f'pull_requests_changelog_sections_{NAME}.json', 'w') as f:
    json.dump(changelog_prs, f, sort_keys=True, indent=2)
