if [[ -z $PR_PACKAGE ]]; then
    package=astropy/astropy
else
    package=${PR_PACKAGE}
fi

if [[ -z $CHANGELOG ]]; then
    changelog=CHANGES.rst
else
    changelog=${CHANGELOG}
fi

if [[ -z $PYEXEC ]]; then
    pyexec=python
else
    pyexec=${PYEXEC}
fi

$pyexec 1.get_merged_prs.py ${package}
$pyexec 2.find_pr_branches.py ${package}
$pyexec 3.find_pr_changelog_section.py ${package} ${changelog}
$pyexec 4.check_consistency.py ${package} > consistency.html
