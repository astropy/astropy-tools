import argparse
import json
import urllib.request

parser = argparse.ArgumentParser()
parser.add_argument('repository', default='astropy/astropy', nargs='?', help='the repository to search for the next PR (default is "astropy/astropy")')

args = parser.parse_args()

with urllib.request.urlopen(f"https://api.github.com/repos/{args.repository}/issues?state=all&sort=created&direction=desc") as response:
    print(f"Next PR number: {json.loads(response.read())[0]['number'] + 1}")
