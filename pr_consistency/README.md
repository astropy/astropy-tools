About
=====

Scripts
-------

The scripts in this directory can be used to check for consistency between pull
request milestones, changelog versions, and which branches pull requests appear
in. Since some of the steps take a while to run, they are split into multiple
scripts:

* ``1.get_merged_prs.py``
* ``2.find_pr_branches.py``
* ``3.find_pr_changelog_section.py``
* ``4.check_consistency.py``

The first three scripts should be run sequentially.

The first script requires authentication for GitHub, for which you can either
use a ``.netrc file``, or you will be prompted for your login details.

These three scripts will produce JSON files which summarize
the required information.

Once this is done, you can then run ``4.check_consistency.py`` to actually run
all the consistency checks. Note that this script has a ``SHOW_VALID`` option.
If set to `False`, this shows only pull requests for which there are issues.

Example
-------

The following shows an example of a typical session. We start off by updating
the JSON file so that it is up-to-date with the pull requests merged into
Astropy:

    $ python 1.get_merged_prs.py 
    Using the following GitHub credentials from ~/.netrc: username/********
    Use these credentials (if not you will be prompted for new credentials)? [Y/n] Y
    Fetching new entry for pull request #5008
    Fetching new entry for pull request #5010
    Fetching new entry for pull request #5012

We now run the second script to find out for all pull requests which
maintenance branches they are included in. Note that this includes some
preliminary information about issues found at this stage (but these can't
typically be fixed since it would mean changing the history):

    $ python 2.find_pr_branches.py 
    Cloning git://github.com/astropy/astropy.git
    Cloning into 'astropy'...
    remote: Counting objects: 103101, done.
    remote: Compressing objects: 100% (13/13), done.
    remote: Total 103101 (delta 2), reused 0 (delta 0), pack-reused 103088
    Receiving objects: 100% (103101/103101), 46.26 MiB | 1.71 MiB/s, done.
    Resolving deltas: 100% (78181/78181), done.
    Checking connectivity... done.
    Switching to branch v0.1.x
    HEAD is now at b97729f Merge pull request #5008 from MSeifert04/docfix
    Branch v0.1.x set up to track remote branch v0.1.x from origin.
    Switched to a new branch 'v0.1.x'
    Switching to branch v0.2.x
    HEAD is now at 3f2b9eb Merge pull request #291 from mdboom/logging/no-astropy-dir
    Branch v0.2.x set up to track remote branch v0.2.x from origin.
    Switched to a new branch 'v0.2.x'
    Switching to branch v0.3.x
    HEAD is now at 6d60c3e Back to development: 0.2.6
    Branch v0.3.x set up to track remote branch v0.3.x from origin.
    Switched to a new branch 'v0.3.x'
    Pull request 663 appears 3 times in branch v0.3.x
    Switching to branch v0.4.x
    HEAD is now at 4202159 Back to development: 0.3.3
    Branch v0.4.x set up to track remote branch v0.4.x from origin.
    Switched to a new branch 'v0.4.x'
    Pull request 663 appears 3 times in branch v0.4.x
    Switching to branch v1.0.x
    HEAD is now at 65444af Back to development: 0.4.7
    Branch v1.0.x set up to track remote branch v1.0.x from origin.
    Switched to a new branch 'v1.0.x'
    Pull request 3766 appears 2 times in branch v1.0.x
    Pull request 663 appears 3 times in branch v1.0.x
    Pull request 4228 appears 2 times in branch v1.0.x
    Switching to branch v1.1.x
    HEAD is now at 0448e5b Merge pull request #3810 from taldcroft/column-scalar
    Branch v1.1.x set up to track remote branch v1.1.x from origin.
    Switched to a new branch 'v1.1.x'
    Pull request 663 appears 3 times in branch v1.1.x
    Switching to branch v1.2.x
    HEAD is now at 955ea32 Merge pull request #4893 from bsipocz/cleanup_changing_log.warn
    Branch v1.2.x set up to track remote branch v1.2.x from origin.
    Switched to a new branch 'v1.2.x'
    Pull request 663 appears 3 times in branch v1.2.x

We then check which sections of the changelog pull requests appear in:

    $ python 3.find_pr_changelog_section.py 
    
Note that we now have three JSON files with information from the above three
scripts:

    $ ls *.json
    merged_pull_requests.json
    pull_requests_branches.json
    pull_requests_changelog_sections.json
    
Finally, we run the script to check the consistency of all the information:

    $ python 4.check_consistency.py 
    #4060 (Milestone: v1.0.10)
      - Milestone is v1.0.10 but change log section is v1.0.5
      - Pull request was included in branch v1.0.x
      - Pull request was included in branch v1.1.x
      - Pull request was included in branch v1.2.x
    #4928 (Milestone: v1.2.0)
      - Labelled as no-changelog-entry-needed and not in changelog
      - Pull request was not included in branch v1.2.x
    #4972 (Milestone: v1.0.10)
      - Labelled as no-changelog-entry-needed and not in changelog
      - Pull request was not included in branch v1.0.x
      - Pull request was not included in branch v1.1.x (but too late to fix)
      - Pull request was not included in branch v1.2.x
    #4984 (Milestone: v1.2.0)
      - Labelled as no-changelog-entry-needed and not in changelog
      - Pull request was not included in branch v1.2.x
    #4995 (Milestone: v1.2.0)
      - Labelled as no-changelog-entry-needed and not in changelog
      - Pull request was not included in branch v1.2.x
    #4997 (Milestone: v1.2.0)
      - Labelled as no-changelog-entry-needed and not in changelog
      - Pull request was not included in branch v1.2.x
    #5008 (Milestone: v1.0.10)
      - Labelled as no-changelog-entry-needed and not in changelog
      - Pull request was not included in branch v1.0.x
      - Pull request was not included in branch v1.1.x (but too late to fix)
      - Pull request was not included in branch v1.2.x

If you want to see all results even pull requests that are valid, you can change
``SHOW_VALID`` to ``True`` in ``4.check_consistency.py ``.

Updating for New Branches
-------------------------

When you add a new branch to these scripts, it is important to add the new 
branch name in *both* of these:

* ``2.find_pr_branches.py``
* ``4.check_consistency.py``

Additionally, in ``4.check_consistency.py`` you'll need to add the branch to
the ``BRANCH_CLOSED`` dictionary.