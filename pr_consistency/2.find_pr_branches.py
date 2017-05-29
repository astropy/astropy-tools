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

from common import branches as br

if sys.argv[1:]:
    REPOSITORY_NAME = sys.argv[1]
else:
    REPOSITORY_NAME = 'astropy/astropy'

print("The repository this script currently works with is '{}'.\n"
      .format(REPOSITORY_NAME))


REPOSITORY = 'git://github.com/{}.git'.format(REPOSITORY_NAME)
NAME = os.path.basename(REPOSITORY_NAME)

DIRTOCLONEIN = tempfile.mkdtemp()  # set this to a non-temp directory to retain the clone between runs
STARTDIR = os.path.abspath('.')

# The branches we are interested in
BRANCHES = br(REPOSITORY_NAME)

# Read in a list of all the PRs
with open('merged_pull_requests_{}.json'.format(NAME)) as merged:
    merged_prs = json.load(merged)

# Set up a dictionary where each key will be a PR and each value will be a list
# of branches in which the PR is present
pr_branches = defaultdict(list)

try:
    # Set up repository
    color_print('Cloning {0}'.format(REPOSITORY), 'green')
    os.chdir(DIRTOCLONEIN)
    if os.path.isdir(NAME):
        # already exists... assume its the right thing
        color_print('"{}" directory already exists - assuming it is an already '
                    'existing clone, so just fetching origin'.format(NAME), 'yellow')
        os.chdir(NAME)
        subprocess.call('git fetch origin', shell=True)
    else:
        subprocess.call('git clone {0}'.format(REPOSITORY), shell=True)
        os.chdir(NAME)

    # Loop over branches and find all PRs in the branch
    for branch in BRANCHES:

        # Change branch
        color_print('Switching to branch {0}'.format(branch), 'green')
        subprocess.call('git reset --hard'.format(), shell=True)
        subprocess.call('git clean -fxd', shell=True)
        subprocess.call('git checkout {0}'.format(branch), shell=True)
        subprocess.call('git reset --hard origin/{}'.format(branch), shell=True)

        # Extract entire log
        log = subprocess.check_output('git log --first-parent', shell=True).decode('utf-8')

        # Check for the presence of the PR in the log
        for pr in merged_prs:
            count = log.count("Merge pull request #{0} ".format(pr))
            if count == 0:
                pass  # not in branch
            else:
                pr_branches[pr].append(branch)
                if count > 1:
                    color_print("Pull request {0} appears {1} times in branch {2}".format(pr, count, branch), 'red')

finally:
    os.chdir(STARTDIR)

with open('pull_requests_branches_{}.json'.format(NAME), 'w') as f:
    json.dump(pr_branches, f, sort_keys=True, indent=2)
