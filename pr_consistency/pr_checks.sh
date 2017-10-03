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

python 1.get_merged_prs.py ${package}
python 2.find_pr_branches.py ${package}
python 3.find_pr_changelog_section.py ${package} ${changelog}
python 4.check_consistency.py ${package} > consistency.html