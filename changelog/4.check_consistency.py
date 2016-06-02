# This script takes the JSON files from the three previous scripts and runs
# a whole bunch of consistency checks described in the comments below.

import json
from datetime import datetime

from astropy.utils.console import color_print


def parse_isoformat(string):
    return datetime.strptime(string, "%Y-%m-%dT%H:%M:%S")

# Only consider PRs merged after this date/time. At the moment, this is the date
# and time at which the v1.0.x branch was created.
START = parse_isoformat('2015-01-27T16:22:59')

# The following option can be toggled to show only pull requests with issues or
# show all pull requests.
SHOW_VALID = False

# The following colors are used to make the output more readabale. CANTFIX is
# used for things that are issues that can never be resolved.
VALID = 'green'
CANTFIX = 'yellow'
INVALID = 'red'
BRANCHES = ['v0.1.x', 'v0.2.x', 'v0.3.x', 'v0.4.x', 'v1.0.x', 'v1.1.x', 'v1.2.x']

# The following gives the dates when branches were closed. This helps us
# understand later whether a pull request could have been backported to a given
# branch.

BRANCH_CLOSED = {
    'v0.1.x': '2012-06-19T02:09:53',
    'v0.2.x': '2013-10-25T12:29:58',
    'v0.3.x': '2014-05-13T12:06:04',
    'v0.4.x': '2015-05-29T15:44:38',
    'v1.0.x': None,
    'v1.1.x': '2016-03-10T01:09:50',
    'v1.2.x': None
}

# We now list some exceptions, starting with manual merges. This gives for the
# specified pull requests the list of branches in which the pull request was
# merged (but which won't show up in the JSON file giving branches for each pull
# request). These pull requests were merged manually without preserving a merge
# commit that includes the pull request number.

# TODO: find a more future-proof way of including manual merges. At the moment,
#       when we add new branches, we'll need to add these branches to all
#       existing manual merges.

MANUAL_MERGES = {
    '4792': ('v1.2.x',),
    '4539': ('v1.0.x',),
    '4423': ('v1.2.x',),
    '4341': ('v1.1.x',),
    '4254': ('v1.0.x',),
    '4719': ('v1.2.x',),
    '4201': ('v1.0.x', 'v1.1.x', 'v1.2.x')
}

# The following gives pull requests we know are missing from certain branches
# and which we will never be able to backport since those branches are closed.

EXPECTED_MISSING = {
    '4266': ('v1.1.x',),  # Forgot to backport to v1.1.x
}

# The following pull requests appear as merged on GitHub but were actually
# marked as merged by another pull request getting merge and including a
# superset of the original commits.

CLOSED_BY_ANOTHER = {
    '3624': '3697',
    '2676': '2680'
}

with open('merged_pull_requests.json') as merged:
    merged_prs = json.load(merged)

with open('pull_requests_changelog_sections.json') as merged:
    changelog_prs = json.load(merged)

with open('pull_requests_branches.json') as merged:
    pr_branches = json.load(merged)

for pr in sorted(merged_prs, key=lambda x: int(x)):

    if parse_isoformat(merged_prs[pr]['merged']) < START:
        continue

    if pr in CLOSED_BY_ANOTHER:
        continue

    # Extract labels and milestones/versions
    labels = merged_prs[pr]['labels']
    milestone = merged_prs[pr]['milestone']
    if milestone is not None and not milestone.startswith('v') and milestone != 'Future':
        milestone = 'v' + milestone
    cl_version = changelog_prs.get(pr, None)
    branches = pr_branches.get(pr, [])

    status = []
    valid = True

    # Make sure that the milestone is consistent with the changelog section, and
    # that this is also consistent with the labels set on the pull request.

    if pr in changelog_prs:
        if 'Affects-dev' in labels:
            pass  # don't print for now since there are too many
            # status.append(('Labelled as affects-dev but in changelog ({0})'.format(cl_version), INVALID))
        elif 'no-changelog-entry-needed' in labels:
            status.append(('Labelled as no-changelog-entry-needed but in changelog', INVALID))
        else:
            if milestone is None:
                status.append(('In changelog ({0}) but not milestoned'.format(cl_version)))
            elif milestone.startswith(cl_version):
                status.append(('In correct section of changelog ({0})'.format(cl_version), VALID))
            else:
                status.append(('Milestone is {0} but change log section is {1}'.format(milestone, cl_version), INVALID))
    else:
        if 'Affects-dev' in labels:
            pass  # don't print for now since there are too many
            # status.append(('Labelled as affects-dev and not in changelog', VALID))
        elif 'no-changelog-entry-needed' in labels:
            status.append(('Labelled as no-changelog-entry-needed and not in changelog', VALID))
        else:
            if milestone is None:
                status.append(('Not in changelog (and no milestone) but not labelled affects-dev', INVALID))
            else:
                if milestone.startswith('v0.1'):
                    status.append(('Not in changelog (but ok since milestoned as {0})'.format(milestone), VALID))
                else:
                    pass  # don't print for now since there are too many
                    # status.append(('Not in changelog (milestoned as {0}) but not labelled as affects-dev'.format(milestone), INVALID))

    # Now check for consistency between PR milestone and branch in which the PR
    # appears - can only check this if the PR milestone is set. If it isn't
    # set, the above will emit a warning, and once a milestone is then set we
    # can rerun this and check for errors below.

    if milestone is not None:

        earliest_expected_branch = milestone[0:4] + '.x'

        if earliest_expected_branch in BRANCHES:

            index = BRANCHES.index(earliest_expected_branch)

            # We now make sure that the PR does NOT appear until ``index``,
            # then is there all the time.

            for i in range(index):
                if BRANCHES[i] in branches:
                    status.append(('Pull request was included in branch {0}'.format(BRANCHES[i]), INVALID))
                else:
                    pass  # all good

            for i in range(index, len(BRANCHES)):
                if BRANCHES[i] in branches:
                    status.append(('Pull request was included in branch {0}'.format(BRANCHES[i]), VALID))
                else:
                    if BRANCHES[i] in MANUAL_MERGES.get(pr, []):
                        status.append(('Pull request was included in branch {0} (manually merged)'.format(BRANCHES[i]), VALID))
                    elif BRANCHES[i] in EXPECTED_MISSING.get(pr, []):
                        status.append(('Pull request was not included in branch {0} (but whitelisted as ok)'.format(BRANCHES[i]), VALID))
                    else:
                        if BRANCH_CLOSED[BRANCHES[i]] is not None:
                            status.append(('Pull request was not included in branch {0} (but too late to fix)'.format(BRANCHES[i]), CANTFIX))
                        else:
                            status.append(('Pull request was not included in branch {0}'.format(BRANCHES[i]), INVALID))

        else:
            pass  # no branch for this milestone yet

    # If SHOW_VALID is False, we want to skip entries which are all valid.
    # Otherwise we want to show both valid and invalid entries.

    if not SHOW_VALID:
        for msg in status:
            if 'red' in msg:
                break
        else:
            continue

    print("#{0} (Milestone: {1})".format(pr, milestone))
    for msg in status:
        color_print('  - ', '', *msg)
