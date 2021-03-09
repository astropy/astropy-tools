# IMPORTANT: The purpose of this script is to update the astropy-helpers
# submodule in all affiliated packages (and a few other packages) that make use
# of the astropy-helpers. This script is not intended to be run by affiliated
# package maintainers, and should only be run with approval of both the
# astropy-helpers and package-template lead maintainers, once an
# astropy-helpers release has been made.

import os
import re
import sys
import shutil
import tempfile
import subprocess
from distutils.version import LooseVersion

from github import Github
from common import get_credentials

try:
    HELPERS_TAG = sys.argv[1]
except IndexError:
    raise IndexError("Please specify the helpers version as argument")


if LooseVersion(HELPERS_TAG) < LooseVersion('v3.0'):
    from helpers_2 import repositories
else:
    from helpers_3 import repositories


BRANCH = 'update-helpers-{0}'.format(HELPERS_TAG)

GITHUB_API_HOST = 'api.github.com'

username, password = get_credentials()
gh = Github(username, password)
user = gh.get_user()

HELPERS_UPDATE_MESSAGE_BODY = re.sub('(\S+)\n', r'\1 ', """
This is an automated update of the astropy-helpers submodule to {0}. This
includes both the update of the astropy-helpers sub-module, and the
``ah_bootstrap.py`` file, if needed.


A full list of changes can be found in the
[changelog](https://github.com/astropy/astropy-helpers/blob/{0}/CHANGES.rst).


*This is intended to be helpful, but if you would prefer to manage these
updates yourself, or if you notice any issues with this automated update,
please let {1} know!*


Similarly to the core package, the v3.0+ releases of astropy-helpers
require Python 3.5+. We will open automated update PRs with
astropy-helpers v3.2.x only for packages that specifically opt in for it
when they start supporting Python 3.5+ only.
Please let {1} know or add your package to the list in
https://github.com/astropy/astropy-procedures/blob/main/update-packages/helpers_3.py

""").strip()


def run_command(command):
    print('-' * 72)
    print("Running '{0}'".format(command))
    ret = subprocess.call(command, shell=True)
    if ret != 0:
        raise Exception("Command '{0}' failed".format(command))


def ensure_fork_exists(repo):
    if repo.owner.login != user.login:
        return user.create_fork(repo)
    else:
        return repo


def open_pull_request(fork, repo):

    # Set up temporary directory
    tmpdir = tempfile.mkdtemp()
    os.chdir(tmpdir)

    # Clone the repository
    run_command('git clone {0}'.format(fork.ssh_url))
    os.chdir(repo.name)

    # Make sure the branch doesn't already exist
    try:
        run_command('git checkout origin/{0}'.format(BRANCH))
    except:
        pass
    else:
        print("Branch {0} already exists".format(BRANCH))
        return

    # Update to the latest upstream main
    print("Updating to the latest upstream main.")
    run_command('git remote add upstream {0}'.format(repo.clone_url))
    run_command('git fetch upstream main')
    run_command('git checkout upstream/main')
    run_command('git checkout -b {0}'.format(BRANCH))

    # Initialize submodule
    print("Initializing submodule.")
    run_command('git submodule init')
    run_command('git submodule update')

    # Check that the repo uses astropy-helpers
    if not os.path.exists('astropy_helpers'):
        print("Repository {0} does not use astropy-helpers".format(repo.name))
        return

    # Update the helpers
    os.chdir('astropy_helpers')
    rev_prev = subprocess.check_output('git rev-list HEAD', shell=True).splitlines()
    run_command('git fetch origin')

    run_command('git checkout {0}'.format(HELPERS_TAG))
    rev_new = subprocess.check_output('git rev-list HEAD', shell=True).splitlines()
    if len(rev_new) <= len(rev_prev):
        print("Repository {0} already has an up-to-date astropy-helpers".format(repo.name))
        return
    os.chdir('..')
    shutil.copy('astropy_helpers/ah_bootstrap.py', 'ah_bootstrap.py')

    run_command('git add astropy_helpers')
    run_command('git add ah_bootstrap.py')
    if os.path.exists('ez_setup.py'):
        run_command('git rm ez_setup.py')
    run_command('git commit -m "Updated astropy-helpers to {0}"'.format(HELPERS_TAG))

    run_command('git push origin {0}'.format(BRANCH))

    print(tmpdir)

    report_user = '@astrofrog'

    if username != 'astrofrog':
        report_user = '@{} or @astrofrog'.format(username)

    repo.create_pull(title='Update astropy-helpers to {0}'.format(HELPERS_TAG),
                     body=HELPERS_UPDATE_MESSAGE_BODY.format(HELPERS_TAG, report_user),
                     base='main',
                     head='{0}:{1}'.format(fork.owner.login, BRANCH))


START_DIR = os.path.abspath('.')

for owner, repository in repositories:
    print("\n########################")
    print("Starting package:     {}/{}".format(owner, repository))
    print("########################\n")


    repo = gh.get_repo("{0}/{1}".format(owner, repository))

    fork = ensure_fork_exists(repo)
    try:
        open_pull_request(fork, repo)
    except:
        pass
    finally:
        os.chdir(START_DIR)
