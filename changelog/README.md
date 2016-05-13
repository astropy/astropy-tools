The scripts in this directory can be used to check for consistency between pull
request milestones, changelog versions, and which branches pull requests appear
in. Since some of the steps take a while to run, they are split into multiple
scripts:

```
1.get_merged_prs.py
2.find_pr_branches.py
3.find_pr_changelog_section.py
4.check_consistency.py
```

The first three scripts should be run sequentially. Note that the
``GITHUB_USER`` and ``GITHUB_PASS`` environment variables should be set for the
first one to work. These three scripts will produce JSON files which summarize
the required information.

Once this is done, you can then run ``4.check_consistency.py`` to actually run
all the consistency checks. Note that this script has a ``SHOW_VALID`` option.
If set to `False`, this shows only pull requests for which there are issues.