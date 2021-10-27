from argparse import ArgumentParser
from datetime import date, datetime
import os

# Package name is github3.py
import github3


def main(token, repo, args,
         verbose=False, dry_run=False, n_min_pr=1,
         oldest_date=None):
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
        too_old = oldest_date
    else:
        # Go back one year from now
        now = datetime.now()
        too_old = date(now.year - 1, now.month, now.day)

    # By default PRs are returned sorted in descending order by date
    # of creation.
    for pr in astropy_org_repo.pull_requests(state='closed'):
        if pr.created_at.date() < date(2019, 12, 31):
            print("Too old, breaking...")
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
                print(author)
            not_in.append(author)
        else:
            if verbose:
                print(f"Already member: {author}")

        already_tried.append(author)

    print(not_in)

    to_add = []
    for author in not_in:
        if verbose:
            print(f"{author} has {pr_count[author]} PRs")
        if pr_count[author] >= n_min_pr:
            to_add.append(author)

    to_add = sorted(to_add)

    for person in to_add:
        gh = g.user(person)
        print(f"Name: {gh.name} GitHub login:{person}")

    for person in to_add:
        if verbose:
            print(f"adding {person} to astropy org...")
        if not dry_run:
            astropy_org.add_or_update_membership(person, role='member')
        else:
            print(f'dry run: would have invited {person}')


if __name__ == '__main__':

    description = ('Check for contributors to astropy packages'
                   ' who are not in the astropy GitHub'
                   ' organization and send them an invitation.\n'
                   'Set the environment variable GITHUB_TOKEN to a valid'
                   ' GitHub token with permission to send invitations'
                   ' to the organization.')

    parser = ArgumentParser(description=description)

    parser.add_argument('repo',
                        help='Name of repository in the astropy GitHub '
                             'organization to check for contributors '
                             'who are not yet members of the organization')

    parser.add_argument('--num-pr', '-n', action='store', default=2, type=int,
                        help='Minimum number of merged PRs contributor must '
                              'have to be added to organization.')

    parser.add_argument('--date', '-d', type=date.fromisoformat,
                        help='Only consider pull requests made after this '
                             'date. Default is one year from date script '
                             ' is run.')

    parser.add_argument('--dry-run',, action='store_true',
                        help='Run the script but do not actually send'
                             ' any invitations.')

    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Display more output while running.')
    args = parser.parse_args()

    print(args)

    token = os.getenv('GITHUB_TOKEN', None)
    if token is None:
        raise RuntimeError('You need to set a GitHub token for this script'
                           ' to work. If you want to see what the script would'
                           ' do without sending invitations use the --dry-run'
                           ' option.')
    main(token, args.repo, )
