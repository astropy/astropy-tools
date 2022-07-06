from argparse import ArgumentParser
from collections import Counter
from datetime import date, datetime
import json
import os

import requests

# Package name is github3.py
import github3


class GitHubOrgAutoInvite:
    def __init__(self, organization, token,
                 verbose=False,
                 dry_run=False,
                 n_min_pr=1,
                 oldest_date=None,
                 min_invite_gap_days=365):
        """
        Generate automatic invitations to an organization based on merged
        pull requests.

        Parameters
        ----------

        organization : str
            Name of the organization on GitHub.

        token : str
            GitHub token with administrative read/write permissions on
            the organization. The account needs sufficient privileges to
            access all information about organization membership.

        verbose : bool, optional
            If `True`, print information about progress.

        dry_run : bool, optional
            If `True`, do everything *except* actually invitations. A
            message is printed instead of issuing the invitation. Intended
            for debugging.

        n_min_pr : int, optional
            Minimum number of pull requests someone not in the organization
            must have had merged to be issued an invitation.

        oldest_date : str, optional
            Date, formatted using ISO format, before which PRs are ignored.

        min_invite_gap_days : int, optional
            Minimum number of days between invitations. Invitations are
            re-sent if it has been at least this many days since the last
            invitation failed and if that failure was because the user never
            responded. If the user has said no, they do not get invited again
            by the bot.
        """
        self.github_connection = github3.login(token=token)
        self.org = self.github_connection.organization(organization)

        # Build lists of categories we should skip invites for
        # If the token does not have sufficient scope then the initialization will fail
        # here.
        self.blocked_users = [b.login for b in self.org.blocked_users()]
        self.open_invitation = [i.login for i in self.org.invitations()]
        self.failed_invites = get_failed_invitations(token, self.org.url)

        # Get list of current members
        self.current_members = [member.login for member in self.org.members()]

        # Set the state for this run
        self.verbose = verbose
        self.dry_run = dry_run
        self.n_min_pr = n_min_pr
        self.oldest_date = oldest_date
        self.min_invite_gap_days = min_invite_gap_days

        # These lists are populated as individual repositories are checked.
        self.pending_invitation = set()

    def process_invites_for_repo(self, repo):
        """
        Get list of contributors to a repository that are not currently
        members of the GitHub organization and send them an
        invitation to join the organization.

        Contributor here means someone who has had a pull request merged.

        Parameters
        ----------

        repo : str
            Name of a repository in the organization to check for
            contributors.
        """
        print_prefix = "\t"
        if self.verbose:
            print(f"\n\nProcessing repository {repo}")

        org_repo = self.github_connection.repository(self.org.login, repo)

        pr_count = {}

        if self.oldest_date is not None:
            if isinstance(self.oldest_date, str):
                oldest_date = date.fromisoformat(self.oldest_date)
            too_old = oldest_date
        else:
            # Go back one year from now
            now = datetime.now()
            too_old = date(now.year - 1, now.month, now.day)

        not_in = []

        if self.verbose:
            print(print_prefix, "Getting merged PRs")

        # By default PRs are returned sorted in descending order by date
        # of creation.
        pr_authors = []
        for pr in org_repo.pull_requests(state='closed'):
            if pr.created_at.date() < too_old:
                if self.verbose:
                    print(print_prefix, f"Reached PRs older than {too_old}, breaking...")
                break
            author = pr.user.login
            pr_authors.append(author)

        # This should reduce author processing to a minimum
        pr_count = Counter(pr_authors)

        for author in pr_count.keys():

            # Stop processing in some cases
            if (author in self.blocked_users):
                continue
            elif (author in self.open_invitation):
                continue
            elif (author == 'ghost'):
                # ghost is the login for any user who has deleted their account
                continue

            if self.verbose:
                print(print_prefix, f"Checking {author}")

            if author not in self.current_members:
                if self.verbose:
                    print(print_prefix, f'\t{author} is not in the astropy org')
                not_in.append(author)
            else:
                if self.verbose:
                    print(print_prefix, f"\t{author} is already in the astropy org")

        if self.verbose:
            print(print_prefix, f'These people from repository {repo} are '
                                f'not in the org {self.org.login}: '
                                f'\n{print_prefix}{print_prefix}{not_in}')

        failed_invitees = self.failed_invites.keys()
        to_add = []
        for author in not_in:
            if author in self.failed_invites:
                reason_to_fail = self._check_send_invitation(self.failed_invites[author])
                if reason_to_fail and self.verbose:
                    print(print_prefix, f"{author} will not be invited because {reason_to_fail}")
                    continue

            if self.verbose:
                print(print_prefix, f"{author} has {pr_count[author]} PRs in repo {repo}, "
                      f"minimum required is {self.n_min_pr}")
            if pr_count[author] >= self.n_min_pr:
                to_add.append(author)

        # No one to add, so keep going
        if not to_add:
            if self.verbose:
                print(print_prefix, f"No one to add from repository {repo}")
            return

        if self.verbose:
            print(print_prefix, f'Adding these people from repository {repo} '
                                f'to the invite list for the org {self.org.login}: '
                                f'\n{print_prefix}{print_prefix}{to_add}')

        self.pending_invitation |= set(to_add)

    def send_invitations(self):
        """
        Actually issue the invitations to the organization
        """
        for person in self.pending_invitation:
            if self.dry_run:
                print(f'DRY RUN: would have invited {person}')
            else:
                self.org.add_or_update_membership(person, role='member')

    def _check_send_invitation(self, failed_invite):
        """
        Decide whether a new invitation should be sent.

        Invitations will only be sent if

        1. The reason for failure is that a previous invitation expired without
           action AND
        2. The expiration was at least ``minimum_gap`` months ago.

        Parameters
        ----------

        failed_invite : dict
            A failed invitation from the GitHub API.

        min_gap_days : int, optional
            Minimum time in days from the expiration of a prior invitation
            until a new invitation will be sent.
        """
        # Don't include the current GitHub cutoff of "7 days" in case they decide
        # to change that in the future.
        expired_fail_message = ("Invitation expired. User did not accept "
                                "this invite for")

        expired = failed_invite['failed_reason'].startswith(expired_fail_message)
        if not expired:
            fail_mesage = ('Failed because previous invitation did not expire. '
                           'Instead, the previous invitation failed because '
                           f'{failed_invite["failed_reason"]}')
            return fail_mesage

        last_expire = datetime.fromisoformat(failed_invite['failed_at'])
        now = datetime.now(tz=last_expire.tzinfo)

        # Add 1 because that is easier than finding fractions of a day.
        # Also, we don't really care about fractional days here.
        elapsed = (now - last_expire).days + 1
        if elapsed < self.min_invite_gap_days:
            fail_message = ('Failed because the time elapsed since the most '
                            f'recent invitation, {elapsed} days, is less '
                            f'than the minimum required gap of '
                            f'{self.min_invite_gap_days} days')
            return fail_message

        # empty string means no need to fail invite
        return ''


# failed_invitations from the GitHub REST API is not part of the github3.py
# API, so it is added here.
def get_failed_invitations(token, org_url):
    """
    Use the GitHub API to get a list of failed invitations.

    NOTE: if failed_invitations ever becomes part of github3.py API
          then this can be removed.

    Parameters
    ----------

    token: str
        GitHub authentication token.

    org_url: str
        URL for API requests for organization of interest.

    Returns
    -------

    List of GitHub invitations that failed
        See https://docs.github.com/en/rest/reference/orgs#list-failed-organization-invitations
        for details of response content.
    """
    headers = {"Authorization": f"token {token}"}
    failed_url = org_url + '/failed_invitations'
    failed_invites = requests.get(failed_url,
                                  headers=headers)
    if failed_invites.status_code != 200:
        raise RuntimeError("Attempt to retrieve failed invitations from "
                           f"{failed_url} resulted in error "
                           f"{failed_invites} {failed_invites.reason}")
    return {f['login']: f for f in failed_invites.json()}


def main(org, token, args):
    """
    Process command line arguments and drive generation of
    invitations.

    Parameters
    ----------

    token : str
        A GitHub token with sufficient permissions to issue invitations
        to the astropy GitHub organization.
    """
    inviter = GitHubOrgAutoInvite(org, token,
                                  verbose=args.verbose,
                                  dry_run=args.dry_run,
                                  n_min_pr=args.num_pr,
                                  oldest_date=args.date,
                                  min_invite_gap_days=args.min_invite_gap)

    for repo in args.repos:
        inviter.process_invites_for_repo(repo)

    inviter.send_invitations()


if __name__ == '__main__':

    description = ('Check for contributors to astropy packages'
                   ' who are not in the astropy GitHub'
                   ' organization and send them an invitation.\n\n'
                   'Set the environment variable GITHUB_TOKEN to a valid'
                   ' GitHub token with permission to send invitations'
                   ' to the organization.')

    parser = ArgumentParser(description=description)

    parser.add_argument('organization',
                        help="Name of the GitHub organization to check for new "
                             "invitees.")

    parser.add_argument('repos', nargs='+',
                        help="One or more repository in this organization "
                             "which are to be checked for new pull requests.")

    parser.add_argument('--num-pr', '-n', action='store',
                        default=1, type=int,
                        help='Minimum number of merged PRs contributor must '
                              'have to be added to organization.')

    parser.add_argument('--date', '-d', type=date.fromisoformat,
                        help='Only consider pull requests made after this '
                             'date. Default is one year from date script '
                             'is run.')

    parser.add_argument('--min-invite-gap', '-m', action='store',
                        default=365, type=int,
                        help='Minimum gap, in days, between the expiration of '
                             'a previous invitation and the sending of a new '
                             'one.')

    parser.add_argument('--dry-run', action='store_true',
                        help='Run the script but do not actually send '
                             'any invitations. The *only* action skipped '
                             'is sending the invitations.')

    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Display more output while running.')

    args = parser.parse_args()

    token = os.getenv('ORG_INVITE_TOKEN', None)
    if token is None:
        raise RuntimeError('You need to set a GitHub token for this script'
                           ' to work. If you want to see what the script would'
                           ' do without sending invitations use the --dry-run'
                           ' option.')

    main(args.organization, token, args)
