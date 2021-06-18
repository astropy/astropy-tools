# This script takes the JSON files from the three previous scripts and runs
# a whole bunch of consistency checks described in the comments below.

import os
import sys
import json
from datetime import datetime
from collections import defaultdict

from astropy.utils.console import color_print

from common import get_branches


def parse_isoformat(string):
    return datetime.strptime(string, "%Y-%m-%dT%H:%M:%S")


# Only consider PRs merged after this date/time. At the moment, this is the
# date and time at which the v1.0.x branch was created.
START = parse_isoformat('2015-01-27T16:22:59')

# The following option can be toggled to show only pull requests with issues or
# show all pull requests.
SHOW_VALID = False

# If set to true, the output is suitable for viewing as a web page instead of
# in the console
HTML_OUTPUT = True

# The repository to show the URL for easy access to PR changelogs.  Can be None
# To not show the url

if sys.argv[1:]:
    REPOSITORY = sys.argv[1]
else:
    REPOSITORY = 'astropy/astropy'

print("The repository this script currently works with is '{}'.\n"
      .format(REPOSITORY))

SHOW_URL_REPO = REPOSITORY

NAME = os.path.basename(REPOSITORY)

# The following colors are used to make the output more readabale. CANTFIX is
# used for things that are issues that can never be resolved.
VALID = 'green'
CANTFIX = 'yellow'
INVALID = 'red'
BRANCHES = get_branches(REPOSITORY)

# The following gives the dates when branches were closed. This helps us
# understand later whether a pull request could have been backported to a given
# branch.

BRANCH_CLOSED_DICT = {'astropy/astropy': {
                          'v0.1.x': parse_isoformat('2012-06-19T02:09:53'),
                          'v0.2.x': parse_isoformat('2013-10-25T12:29:58'),
                          'v0.3.x': parse_isoformat('2014-05-13T12:06:04'),
                          'v0.4.x': parse_isoformat('2015-05-29T15:44:38'),
                          'v1.0.x': parse_isoformat('2017-05-29T23:44:38'),
                          'v1.1.x': parse_isoformat('2016-03-10T01:09:50'),
                          'v1.2.x': parse_isoformat('2016-12-23T05:32:04'),
                          'v1.3.x': parse_isoformat('2017-05-29T23:44:38'),
                          'v2.0.x': parse_isoformat('2019-11-10T16:00:00'),
                          'v3.0.x': parse_isoformat('2018-10-18T16:00:00'),
                          'v3.1.x': parse_isoformat('2019-04-15T16:00:00'),
                          'v3.2.x': parse_isoformat('2019-11-10T16:00:00'),
                          'v4.0.x': None,
                          'v4.1.x': parse_isoformat('2020-11-25T06:46:46'),
                          'v4.2.x': None,
                          'v4.3.x': None},
                      }

BRANCH_CLOSED_DICT['astropy/astropy-helpers'] = BRANCH_CLOSED_DICT['astropy/astropy']

# We now list some exceptions, starting with manual merges/backports. This
# gives for the specified pull requests the list of branches in which the
# pull request was merged or was backported manually (but which won't show
# up in the JSON file giving branches for each pull request). These pull
# requests were merged manually without preserving a merge commit that
# includes the original pull request number.

# TODO: find a more future-proof way of including manual merges. At the moment,
#       when we add new branches, we'll need to add these branches to all
#       existing manual merges.
MANUAL_MERGES_DICT = {
    'astropy/astropy': {'8264': ('v2.0.x',),
                        '7575': ('v2.0.x',),
                        '7336': ('v2.0.x',),
                        '7274': ('v2.0.x',),
                        '6605': ('v2.0.x',),
                        '6555': ('v2.0.x',),
                        '6423': ('v2.0.x',),
                        '4792': ('v1.2.x',),
                        '4539': ('v1.0.x',),
                        '4423': ('v1.2.x',),
                        '4341': ('v1.1.x',),
                        '4254': ('v1.0.x',),
                        '4719': ('v1.2.x',),
                        '4201': ('v1.0.x', 'v1.1.x', 'v1.2.x'),
                        '9183': ('v3.2.x', 'v4.0.x', 'v4.1.x', 'v4.2.x'),
                        '10437': ('v4.0.x',),
                        '11108': ('v4.2.x'),
                        '11128': ('v4.2.x'),
                        '11145': ('v4.2.x'),
                        '11389': ('v4.2.x'),
                        '11391': ('v4.2.x'),
                        '11401': ('v4.2.x'),
                        '11250': ('v4.2.x'),
                        '9183': ('v4.3.x'),
                        '11756': ('v4.3.x'), # bot did this one in 11766
                        '11724': ('v4.3.x'), # bot did this one in 11799
                        '11756': ('v4.3.x'), # bot did this one in 11766
                    },
    'astropy/astropy-helpers': {'205': ('v1.1.x', 'v1.2.x', 'v1.3.x', 'v2.0.x',
                                        'v3.0.x', 'v3.1.x', 'v3.2.x', 'v4.0.x'),
                                '172': ('v1.1.x', 'v1.2.x', 'v1.3.x', 'v2.0.x',
                                        'v3.0.x', 'v3.1.x', 'v3.2.x', 'v4.0.x'),
                                '206': ('v1.0.x', 'v1.1.x', 'v1.2.x', 'v1.3.x',
                                        'v2.0.x',
                                        'v3.0.x', 'v3.1.x', 'v3.2.x', 'v4.0.x'),
                                '362': ('v2.0.x')}
}


BRANCH_CLOSED = {}
MANUAL_MERGES = {}

try:
    BRANCH_CLOSED = BRANCH_CLOSED_DICT[REPOSITORY]
    MANUAL_MERGES = MANUAL_MERGES_DICT[REPOSITORY]
except KeyError:
    pass

# The following gives pull requests we know are missing from certain branches
# and which we will never be able to backport since those branches are closed.

EXPECTED_MISSING = {
    '4266': ('v1.1.x',),  # Forgot to backport to v1.1.x
}

REVERTED_FROM_BRANCH ={
    '6277': ('v2.0.x',),  # PR has been reverted from this branch
}

# The following pull requests appear as merged on GitHub but were actually
# marked as merged by another pull request getting merge and including a
# superset of the original commits.

CLOSED_BY_ANOTHER = {
    '3624': '3697',
    '2676': '2680'
}

with open('merged_pull_requests_{}.json'.format(NAME)) as merged:
    merged_prs = json.load(merged)

with open('pull_requests_changelog_sections_{}.json'.format(NAME)) as merged:
    changelog_prs = json.load(merged)

with open('pull_requests_branches_{}.json'.format(NAME)) as merged:
    pr_branches = json.load(merged)


if HTML_OUTPUT:
    print('<!DOCTYPE html>\n<title>Astropy Consistency Check Report</title>'
          '\n\n<h1>Main report for repository {}</h1>'.format(REPOSITORY))
else:
    color_print('Main report:', 'blue')

backports = defaultdict(list)

for pr in sorted(merged_prs, key=lambda pr: merged_prs[pr]['merged']):

    if 'unusual-merge-dealt-with' in merged_prs[pr]['labels']:
        # This label indicates problematic PRs that have been checked
        # manually and don't need to be considered here.
        continue

    merge_date = parse_isoformat(merged_prs[pr]['merged'])

    if merge_date < START:
        continue

    if pr in CLOSED_BY_ANOTHER:
        continue

    # Extract labels and milestones/versions
    labels = merged_prs[pr]['labels']
    milestone = merged_prs[pr]['milestone']
    if milestone is not None and not milestone.startswith('v') and milestone != 'Future':
        milestone = 'v' + milestone

    cl_version = changelog_prs.get(pr, None)

    if cl_version:
        # Ignore RC status in changelog, those are temporary measures
        cl_version = cl_version.split('rc')[0]

    branches = pr_branches.get(pr, [])

    status = []
    valid = True

    # Make sure that the milestone is consistent with the changelog section, and
    # that this is also consistent with the labels set on the pull request.

    affect_dev = {'Affects-dev', 'affects-dev', 'affect-dev', 'Affect-dev'}
    affect_dev_in_labels = len(affect_dev.intersection(set(labels))) > 0

    if pr in changelog_prs:
        if affect_dev_in_labels:
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
        if affect_dev_in_labels:
            status.append(('Labelled as affects-dev and not in changelog', VALID))
        elif 'no-changelog-entry-needed' in labels:
            status.append(('Labelled as no-changelog-entry-needed and not in changelog', VALID))
        else:
            if milestone is None:
                status.append(('Not in changelog (and no milestone) but not labelled affects-dev', INVALID))
            else:
                if milestone.startswith('v0.1'):
                    status.append(('Not in changelog (but ok since milestoned as {0})'.format(milestone), VALID))
                else:
                    status.append(('Not in changelog (milestoned as {0}) but not labelled as affects-dev'.format(milestone), INVALID))

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
                    if BRANCHES[i] in REVERTED_FROM_BRANCH.get(pr, []):
                        status.append(('Pull request was in branc {0} but has been reverted later.'.format(BRANCHES[i]), VALID))
                    else:
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
                            if merge_date > BRANCH_CLOSED[BRANCHES[i]]:
                                status.append(('Pull request was not included in branch {0} (but was merged after branch closed)'.format(BRANCHES[i]), VALID))
                            else:
                                status.append(('Pull request was not included in branch {0} (but too late to fix)'.format(BRANCHES[i]), CANTFIX))
                        else:
                            status.append(('Pull request was not included in branch {0}. Backport command included below.'.format(BRANCHES[i]), INVALID))
                            backports[BRANCHES[i]].append(pr)

        else:
            pass  # no branch for this milestone yet

    # If SHOW_VALID is False, we want to skip entries which are all valid.
    # Otherwise we want to show both valid and invalid entries.

    if not SHOW_VALID:
        for msg in status:
            if INVALID in msg:
                break
        else:
            continue

    url = ''
    if SHOW_URL_REPO:
        url = 'https://github.com/{}/issues/{}'.format(SHOW_URL_REPO, pr)
    if HTML_OUTPUT:
        print('<p>')
        print('<a href="{2}">#{0}</a> (Milestone: {1})'.format(pr, milestone, url))
        print('<ul>')
        for msg, color in status:
            print('<li style="color:{color};">{msg}</li>'.format(msg=msg, color=color))
        print('</ul>\n</p>')
    else:
        print("#{0}{2} (Milestone: {1})".format(pr, milestone, ' ('+url+')'))
        for msg in status:
            color_print('  - ', '', *msg)

for version in sorted(backports.keys()):
    if HTML_OUTPUT:
        print('<h1>Backports to {}</h1>'.format(version))
        print('{} merges in total. These are in merge order:'.format(
            len(backports[version])))
        print('<pre>')
        for pr in backports[version]:
            prorurl = '#{}'.format('pr')
            if SHOW_URL_REPO:
                url = 'https://github.com/{}/issues/{}'.format(SHOW_URL_REPO, pr)
                prorurl = '<a href="{}">#{}</a>'.format(url, pr)

            print('# Pull request {}: {}'.format(prorurl, merged_prs[pr]['title']))
            print('git cherry-pick -m 1 {}'.format(merged_prs[pr]['merge_commit']))
        print('</pre>')
    else:
        color_print('Backports to {0} (in merge order)'.format(version), 'blue')
        for pr in backports[version]:
            print('# Pull request #{0}: {1}'.format(pr, merged_prs[pr]['title']))
            print('git cherry-pick -m 1 {0}'.format(merged_prs[pr]['merge_commit']))
