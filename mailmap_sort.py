"""
This script sorts a .mailmap file by name and email. This is meant to be used
with the mailmap_check.py script when updating the .mailmap file.

Usage:

    python mailmap_sort.py <mailmap path>
"""

# Standard library
import pathlib
import sys

# Third-party
import numpy as np


if len(sys.argv) != 2:
    raise ValueError(
        "Pass in a single command-line argument: the path to the mailmap file"
    )

mailmap_path = pathlib.Path(sys.argv[1])
if not mailmap_path.exists():
    raise RuntimeError(f"Mailmap path does not exist {mailmap_path}")

sortable = []
with open(mailmap_path, 'r') as f:
    lines = [x.strip() for x in f.readlines()]
    for line in lines:
        name, *name_emails = [
            x.replace('<', '').replace('>', '').strip()
            for x in line.split('<')
        ]
        name_emails = [x.lower() for x in name_emails]
        name = f"{name}{len(name_emails)} " + " ".join(name_emails)
        sortable.append(name)

for line in np.array(lines)[np.argsort(sortable)]:
    print(line)
