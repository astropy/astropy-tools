"""
IMPORTANT NOTICE
================
The purpose of this script is to update the astropy-helpers
submodule in all affiliated packages (and a few other packages) that make use
of the astropy-helpers. This script is not intended to be run by affiliated
package maintainers, and should only be run with approval of both the
astropy-helpers and package-template lead maintainers, once an
astropy-helpers release has been made.

"""
import os
import re
import subprocess
from distutils.version import LooseVersion

from batchpr import Updater

GITHUB_TOKEN = 'fixme'

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
astropy-helpers v3.1.x only for packages that specifically opt in for it
when they start supporting Python 3.5+ only.
Please let {1} know or add your package to the list in
https://github.com/astropy/astropy-procedures/blob/master/update-packages/helpers_3.py

""").strip()


class HelpersUpdater(Updater):
    """Class to handle batch updates of astropy-helpers."""
    helpers_tag = ''  # This is set by user running the script.

    def process_repo(self):
        """Update astropy-helpers."""
        # Check that the repo uses astropy-helpers
        if os.path.exists('astropy_helpers'):
            status = True
            cmd_rev_list = ['git', 'rev-list', 'HEAD']

            os.chdir('astropy_helpers')
            rev_prev = subprocess.check_output(cmd_rev_list).splitlines()
            self.run_command('git fetch origin')

            self.run_command(f'git checkout {self.helpers_tag}')
            rev_new = subprocess.check_output(cmd_rev_list).splitlines()
            if len(rev_new) <= len(rev_prev):
                print(f"Repository {self.repo.name} already has "
                      "an up-to-date astropy-helpers")
                return False
            os.chdir('..')
            self.copy('astropy_helpers/ah_bootstrap.py', 'ah_bootstrap.py')

            self.run_command('git add astropy_helpers')
            self.run_command('git add ah_bootstrap.py')
            if os.path.exists('ez_setup.py'):
                self.run_command('git rm ez_setup.py')

        else:
            status = False
            print(f"Repository {self.repo.name} does not use astropy-helpers")

        return status

    @property
    def commit_message(self):
        return f"Updated astropy-helpers to {self.helpers_tag}"

    @property
    def branch_name(self):
        return f'update-helpers-{self.helpers_tag}'

    @property
    def pull_request_title(self):
        return f"Update astropy-helpers to {self.helpers_tag}"

    @property
    def pull_request_body(self):
        default_user = 'astrofrog'
        username = self.user.login

        if username != default_user:
            report_user = f'@{username} or @{default_user}'
        else:
            report_user = f'@{default_user}'

        return HELPERS_UPDATE_MESSAGE_BODY.format(
            self.helpers_tag, report_user)


def main(helpers_tag, dry_run=False, verbose=False):
    """Main driver for the helpers batch updater.

    Parameters
    ----------
    helpers_tag : str
        Tag of astropy-helpers to update to.

    dry_run : bool
        If `True`, the updater does not push the feature branch out nor
        open the actual pull request but still runs all the other steps
        (i.e., forking, branching, and committing the changes).

    verbose : bool
        Print command output to screen.
        If `False`, it will only be printed on failure.

    """
    if LooseVersion(helpers_tag) < LooseVersion('v3.0'):
        from helpers_2 import repositories
    else:
        from helpers_3 import repositories

    all_repos = [f'{owner}/{repository}' for owner, repository in repositories]
    pr_helper = HelpersUpdater(GITHUB_TOKEN, dry_run=dry_run, verbose=verbose)
    pr_helper.helpers_tag = helpers_tag
    pr_helper.run(all_repos)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'helpers_tag', help='Please specify the helpers version as argument')
    parser.add_argument(
        '--dry', action='store_true', help='Dry run only')
    parser.add_argument(
        '--verbose', action='store_true', help='Verbose output')
    args = parser.parse_args()

    main(args.helpers_tag, dry_run=args.dry, verbose=args.verbose)
