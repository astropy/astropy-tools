import sys

try:
    from github3 import GitHub
except ImportError:
    raise ImportError('Please conda or pip install github3.py')

if len(sys.argv) == 2:
    repository = sys.argv[1]
elif len(sys.argv) > 2:
    print("Usage: next_pr_number.py <repository>")
    sys.exit(1)
else:
    repository = ('astropy', 'astropy')

gh = GitHub()
repo = gh.repository(*repository)
for issue in repo.issues(sort='created', state='all'):
    print(issue.number + 1)
    break
