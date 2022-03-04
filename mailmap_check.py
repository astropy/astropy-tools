"""
This script finds all authors that have committed to the Astropy core package
and compares against the .mailmap file in the core package repository. This
only checks whether emails in the git commit author list are present in the
mailmap or not, and prints name/email pairs for any missing emails.

Usage:

    python mailmap_check.py <astropy repo path>
"""

# Standard library
import pathlib
import sys

# Third-party
import astropy.table as at
from git import Repo

if len(sys.argv) != 2:
    raise ValueError(
        "Pass in a single command-line argument: the path to the cloned "
        "astropy core repository"
    )

astropy_repo_path = pathlib.Path(sys.argv[1])
if not astropy_repo_path.exists():
    raise RuntimeError(f"Astropy repo path does not exist {astropy_repo_path}")

mailmap_path = astropy_repo_path / '.mailmap'
repo = Repo(astropy_repo_path)

all_authors = []
for commit in repo.iter_commits():
    all_authors.append({
        'name': commit.author.name.strip(),
        'email': commit.author.email.strip().lower()
    })
all_authors = at.Table(all_authors)
all_authors = at.unique(all_authors, keys='email')

mailmap_path = astropy_repo_path / '.mailmap'

email_to_name = {}
with open(mailmap_path, 'r') as f:
    for line in f:
        name, *name_emails = [
            x.replace('<', '').replace('>', '').strip()
            for x in line.split('<')
        ]
        name_emails = [x.lower() for x in name_emails]

        for _email in name_emails:
            if _email in email_to_name and name != email_to_name[_email]:
                raise ValueError(f"name: {name}, email: {_email}")
            email_to_name[_email] = name

missing_authors = []
for author in all_authors:
    if author['email'] not in email_to_name:
        missing_authors.append(dict(author))
missing_authors = at.Table(missing_authors)
missing_authors.sort('name')
for author in missing_authors:
    print(f"{author['name']: <29}<{author['email']}>")
