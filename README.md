# astropy-tools

This repository stores scripts for development and advertising,
or similar tools used by the Astropy project. Some of the tools
may be useful in other contexts, but stability is not guaranteed.

### add_contributors_to_org.py

:no_entry: This is broken! See [GitHub Issue 178](https://github.com/astropy/astropy-tools/issues/178).

This is used by [Invite organization members based on merged PRs](https://github.com/astropy/astropy-tools/actions/workflows/update_org_members.yml).

### next_pr_number.py

✔️ Probably the most useful tool we have here.

Find the next PR number for a given repo before you even open the PR.
This is useful when you want to write the change log in advance
that requires a PR number attached.

```
python next_pr_number.py org/repo
```

If `org/repo` is not given, it looks in `astropy/astropy`.

### astropy_certificates

✔️ Nadia used this for [Astropy workshop in Bulgaria](https://github.com/astropy/astropy-project/issues/345).

This directory contains materials to generate a "Certificate of Achievement"
with Astropy logo on it. This is useful when Astropy runs a workshop
and the host requests that certificates be given out for a reason or another.
This certificate is **not** official and should not be used in resumes and so on.

### pr_consistency

:warning: Its future is being discussed at
[GitHub Issue 176](https://github.com/astropy/astropy-tools/issues/176).

A series of scripts to check consistency in backporting pull requests
back to release branch(es). They are used by
[Run PR changelog consistency check scripts](https://github.com/astropy/astropy-tools/actions/workflows/pr_consistency.yml).

### astropy_usage

:warning: Might need updating.

The script within is used to generate usage statistics for `astropy`.

p.s. Maybe we want to switch to https://devstats.scientific-python.org/ ?

### visualizations_demographics

:warning: Might need updating.

Scripts to generate plots for talks about Astropy involving demographics.

### discontinued_usage

:no_entry: The scripts here are no longer used and kept to preserve history.
We reserve the rights to remove them in the future without notice
(even then, they will still be available in older versions anyway).
