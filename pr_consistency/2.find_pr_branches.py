# The purpose of this script is to check all the maintenance branches of the
# given repository, and find which pull requests are included in which
# branches. The output is a JSON file that contains for each pull request the
# list of all branches in which it is included. We look specifically for the
# message "Merge pull request #xxxx " in commit messages, so this is not
# completely foolproof, but seems to work for now.

import os
import sys
import json
import subprocess
import tempfile
from collections import defaultdict

from astropy.utils.console import color_print

from common import get_branches

if sys.argv[1:]:
    REPOSITORY_NAME = sys.argv[1]
else:
    REPOSITORY_NAME = 'astropy/astropy'

print("The repository this script currently works with is '{}'.\n"
      .format(REPOSITORY_NAME))


REPOSITORY = f'git://github.com/{REPOSITORY_NAME}.git'
NAME = os.path.basename(REPOSITORY_NAME)

DIRTOCLONEIN = tempfile.mkdtemp()  # set this to a non-temp directory to retain the clone between runs
ORIGIN = 'origin'  # set this to None to not fetch anything but rather use the directory as-is.

STARTDIR = os.path.abspath('.')

# The branches we are interested in
BRANCHES = get_branches(REPOSITORY_NAME)

# Read in a list of all the PRs
with open(f'merged_pull_requests_{NAME}.json') as merged:
    merged_prs = json.load(merged)

# Set up a dictionary where each key will be a PR and each value will be a list
# of branches in which the PR is present
pr_branches = defaultdict(list)


def check_merged_pr(log, msg):
    count = log.count(msg)
    if count > 0:
        pr_branches[pr].append(branch)
        if count > 1:
            color_print(f"Pull request {pr} appears {count} times in branch {branch}", 'red')
    return count


try:
    # Set up repository
    color_print(f'Cloning {REPOSITORY}', 'green')
    os.chdir(DIRTOCLONEIN)
    if os.path.isdir(NAME):
        # already exists... assume its the right thing
        color_print('"{}" directory already exists - assuming it is an already '
                    'existing clone'.format(NAME), 'yellow')
        os.chdir(NAME)
        if ORIGIN:
            subprocess.call(f'git fetch {ORIGIN}', shell=True)
    else:
        subprocess.call(f'git clone {REPOSITORY}', shell=True)
        os.chdir(NAME)

    # Loop over branches and find all PRs in the branch
    for branch in BRANCHES:

        # Change branch
        color_print(f'Switching to branch {branch}', 'green')
        subprocess.call(f'git reset --hard', shell=True)
        subprocess.call('git clean -fxd', shell=True)
        subprocess.call(f'git checkout {branch}', shell=True)
        if ORIGIN:
            subprocess.call(f'git reset --hard {ORIGIN}/{branch}', shell=True)

        # Extract log:
        # With merges only for the historical backport script
        log_merges = subprocess.check_output('git log --first-parent', shell=True).decode('utf-8')
        # Full log for the backport bot
        log_full = subprocess.check_output('git log', shell=True).decode('utf-8')

        # Check for the presence of the PR in the log
        for pr in merged_prs:
            count = check_merged_pr(log_merges, f"Merge pull request #{pr} ")
            if count == 0:
                check_merged_pr(log_full, f"Backport PR #{pr}:")

finally:
    os.chdir(STARTDIR)

with open(f'pull_requests_branches_{NAME}.json', 'w') as f:
    json.dump(pr_branches, f, sort_keys=True, indent=2)
