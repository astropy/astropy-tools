import sys
import time
import pickle
import requests

from github import Github, GithubException

from common import get_credentials

step_size = 100
search_phrase = '"from astropy" import OR "import astropy"'

username, password = get_credentials()

gh = Github(username, password)
total_repo = gh.search_code(search_phrase).totalCount


if len(sys.argv) > 1:
    filename = sys.argv[1]
    print("Loading previous results from {}".format(filename))
    with open(filename, 'rb') as f:
        saved_results = pickle.load(f)
    step, queried_results, gh_repo, gh_name, missed_results = saved_results
else:
    step = 0
    queried_results = 0
    gh_repo = set()
    gh_name = set()
    missed_results = 0

print("Total number of search results: {}".format(total_repo))


# We need to limit the search by repo size as the results are limited to 1000.
# (and astropy is imported in 58K+ repositories.

while queried_results + missed_results < total_repo:
    queried_results_rollback = queried_results
    gh_search_result = gh.search_code('{} size:{}..{}'.format(
        search_phrase, step * step_size, (step + 1) * step_size))
    current_total = gh_search_result.totalCount

    if current_total > 1000:
        print("Use smaller step_size total count is {} for size {}..{}".format(
            current_total, step * step_size, (step + 1) * step_size))
        missed_results += current_total - 1000

    try:
        for i in gh_search_result:
            gh_full_name = i.repository.full_name
            gh_repo.add(gh_full_name)
            gh_name.add(gh_full_name.split('/')[-1])
            queried_results += 1
            # This is an ugly hack to work around the API limits
            time.sleep(0.4)
    except GithubException:
        print("Finished search up until step {} for a total of {} repos. "
              "Search failed after the {}th repo.".format(
                  step, queried_results_rollback, queried_results))
        queried_results = queried_results_rollback
        with open('usage_results.pkl', 'wb') as f:
            results = (step, queried_results, gh_repo, gh_name, missed_results)
            pickle.dump(results, f)
        raise

    step += 1

    # save partial results at each step
    with open('usage_results.pkl', 'wb') as f:
        results = (step, queried_results, gh_repo, gh_name, missed_results)
        pickle.dump(results, f)

    time.sleep(30)


pypi_name = set()
checked_names = set()

for i, name in enumerate(gh_name):
    response = requests.get("http://pypi.python.org/pypi/{}/json".format(name))
    if response.status_code == 200:
        pypi_name.add(name)
    checked_names.add(name)

    # Save partial results
    if i % 500 == 0:
        with open('pypi_results.pkl', 'wb') as f:
            results = (pypi_name, checked_names)
            pickle.dump(results, f)

with open('pypi_results.pkl', 'wb') as f:
    results = (pypi_name, checked_names)
    pickle.dump(results, f)

print("Unique GitHub repos: {}\n"
      "Projects on PyPI: {}\n".format(
          len(gh_repo), len(pypi_name)))
