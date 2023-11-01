import requests
from github import Github
from common import get_credentials

username, password = get_credentials()
gh = Github(username, password)

gh_search_result = gh.search_code('filename:.travis.yml "astropy/ci-helpers"')

gh_repo = []
gh_name = []

for i in gh_search_result:
    gh_repo.append(i.repository.full_name)
    gh_name.append(i.repository.name)

gh_name = set(gh_name)

pypi_name = []

for i in gh_name:
    response = requests.get("http://pypi.python.org/pypi/{}/json".format(i))
    if response.status_code == 200:
        pypi_name.append(i)


print(len(gh_name), len(pypi_name))
