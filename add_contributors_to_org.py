from argparse import ArgumentParser
from datetime import date, datetime
import json
import os

import requests

# Package name is github3.py
import github3


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


def check_send_invitation(failed_invite, min_gap_days=365):
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
        fail_mesage

    last_expire = datetime.fromisoformat(failed_invite['failed_at'])
    now = datetime.now(tz=last_expire.tzinfo)

    # Add 1 because that is easier than finding fractions of a day.
    # Also, we don't really care about fractional days here.
    elapsed = (now - last_expire).days + 1
    if elapsed < min_gap_days:
        fail_message = ('Failed because the time elapsed since the most '
                        f'recent invitation, {elapsed} days, is less '
                        f'than the minimum required gap of '
                        f'{min_gap_days} days')
        return fail_message

    # empty string means no need to fail invite
    return ''


def process_invites_for_repo(token, repo,
                             verbose=False, dry_run=False, n_min_pr=1,
                             oldest_date=None, min_invite_gap_days=365):
    """
    Get list of contributors to a repository that are not currently
    members of the Astropy GitHub organization and send them an
    invitation to join the organization.

    Contributor here means someone who has had a pull request merged.

    Parameters
    ----------

    token : str
        A GitHub token with adequate permissions to send invitations to
        the Astropy GitHub organization.

    repo : str
        Name of a repository in the Astropy organization to check for
        contributors.
    """

    g = github3.login(token=token)
    astropy_org_repo = g.repository('astropy', repo)
    astropy_org = g.organization('astropy')

    already_tried = []

    not_in = []

    pr_count = {}

    if oldest_date is not None:
        if isinstance(oldest_date, str):
            oldest_date = date.fromisoformat(oldest_date)
        too_old = oldest_date
    else:
        # Go back one year from now
        now = datetime.now()
        too_old = date(now.year - 1, now.month, now.day)

    # By default PRs are returned sorted in descending order by date
    # of creation.
    if verbose:
        print("Getting merged PRs")

    for pr in astropy_org_repo.pull_requests(state='closed'):
        if pr.created_at.date() < too_old:
            if verbose:
                print(f"Reached PRs older than {too_old}, breaking...")
            break

        author = pr.user.login

        if (author in already_tried):
            pr_count[author] += 1
            continue
        elif (author == 'ghost'):
            # ghost is the login for any user who has deleted their account
            continue

        pr_count[author] = 1

        if verbose:
            print(f"Checking {author}")

        if not astropy_org.is_member(author):
            if verbose:
                print(f'\t{author} is not in the astropy org')
            not_in.append(author)
        else:
            if verbose:
                print(f"\t{author} is already in the astropy org")

        already_tried.append(author)

    if verbose:
        print(f'These people are not in the astropy org: {not_in}')
        print('Checking number of pull requests')

    failed_invites = get_failed_invitations(token, astropy_org.url)
    failed_invitees = failed_invites.keys()
    to_add = []
    for author in not_in:
        if author in failed_invitees:
            reason_to_fail = check_send_invitation(failed_invites[author])
            if reason_to_fail:
                print(f"{author} will not be invited because {reason_to_fail}")
                continue

        if verbose:
            print(f"{author} has {pr_count[author]} PRs")
        if pr_count[author] >= n_min_pr:
            to_add.append(author)

    to_add = sorted(to_add)

    if verbose:
        print(f'Inviting these people to join the astropy org: {to_add}')

    for person in to_add:
        if verbose:
            print(f"\tadding {person} to astropy org...")
        if not dry_run:
            astropy_org.add_or_update_membership(person, role='member')
        else:
            print(f'\tDRY RUN: would have invited {person}')


def main(token, args):
    """
    Process command line arguments and drive generation of
    invitations.

    Parameters
    ----------

    token : str
        A GitHub token with sufficient permissions to issue invitations
        to the astropy GitHub organization.
    """

    # Figure out whether we got a repo name or a json file.
    repo_or_json = args.repo_or_json_file

    try:
        with open(repo_or_json) as f:
            repos = json.load(f)
    except FileNotFoundError:
        # Assume we got a repo name
        repos = {}

    if not repos:
        # No json file, so construct dict from arguments
        repos = {
            repo_or_json: {
                "min_merged_prs": args.num_pr,
                "only_prs_since": args.date,
                "min_time_between_invites_days": args.min_invite_gap,
            }
        }
        if args.verbose:
            print(f'Constructed settings {repos}')

    for repo, settings in repos.items():
        if args.verbose:
            print(f'Processing {repo=}')
        process_invites_for_repo(token, repo,
                                 n_min_pr=settings["min_merged_prs"],
                                 oldest_date=settings["only_prs_since"],
                                 min_invite_gap_days=settings['min_time_between_invites_days'],
                                 verbose=args.verbose,
                                 dry_run=args.dry_run)



if __name__ == '__main__':

    description = ('Check for contributors to astropy packages'
                   ' who are not in the astropy GitHub'
                   ' organization and send them an invitation.\n\n'
                   'Set the environment variable GITHUB_TOKEN to a valid'
                   ' GitHub token with permission to send invitations'
                   ' to the organization.')

    parser = ArgumentParser(description=description)

    parser.add_argument('repo_or_json_file',
                        help='Name of repository in the astropy GitHub '
                             'organization to check for contributors '
                             'who are not yet members of the organization. '
                             '\nAlternatively, a json file can be specified '
                             'that includes one or more repo names and '
                             'settings for each repo.\n\n'
                             'NOTE: Settings in a json file override command '
                             'line settings.')

    parser.add_argument('--num-pr', '-n', action='store',
                        default=2, type=int,
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

    token = os.getenv('GITHUB_TOKEN', None)
    if token is None:
        raise RuntimeError('You need to set a GitHub token for this script'
                           ' to work. If you want to see what the script would'
                           ' do without sending invitations use the --dry-run'
                           ' option.')

    main(token, args)
    # main(token, args.repo, verbose=args.verbose,
    #      dry_run=args.dry_run, n_min_pr=args.num_pr, oldest_date=args.date)
