import sys
import json
import urllib.request

if len(sys.argv) == 2:
    repository = sys.argv[1]
elif len(sys.argv) > 2:
    print("Usage: next_pr_number.py <repository>")
    sys.exit(1)
else:
    repository = 'astropy/astropy'

with urllib.request.urlopen(f"https://api.github.com/repos/{repository}/issues") as response: 
    print(f"Next PR number: {json.loads(response.read())[0]['number'] + 1}")
