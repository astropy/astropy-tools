import sys
from github import Github

if len(sys.argv) == 2:
    repository = sys.argv[1]
elif len(sys.argv) > 2:
    print("Usage: next_pr_number.py <repository>")
    sys.exit(1)
else:
    repository = 'astropy/astropy'

gh = Github()
repo = gh.get_repo(repository)
pl = repo.get_issues(sort='created', state='all')
print("Next PR number: {0}".format(pl.get_page(0)[0].number + 1))
