#! /usr/bin/env python

"""This module collects contribution data for astropy-affiliated
packages and creates plots that show the number of contributors over
time.

Plots are made for individual packages as well as an aggregate of all
astropy-affiliated packages.

Plots are saved to a `plots/` directory alongside this module.

Authors
-------

    Matthew Bourque

Use
---

    This module is intended to be executed on the command line as such:

        >>> python contributor_plots.py

    The user must have a `config.yaml` file along side of this module
    that contains one key/value pair: a `token` that points to the
    user's GitHub auth token.
"""

import datetime
import json
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import requests
import urllib.request
import yaml


def create_aggregate_plot(package_contributions):
    """Creates a plot that shows the aggregate number of contributors
    over all astropy-affiliated packages.

    Parameters
    ----------
    package_contributors : dict
        A dictrionary whose keys are package names and whose values are
        a list of dates in which a new contributor happened.
    """

    new_contributors = []
    for package in package_contributions:
        new_contributors.extend(package_contributions[package].values())

    new_contributors = sorted(new_contributors)
    num_contributors = list(range(len(new_contributors)))

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(new_contributors, num_contributors)
    ax.set_title('All astropy Affiliated Packages')
    ax.set_ylabel('# of contributors')
    plt.savefig(f'plots/all.png')
    plt.close()


def create_package_plot(package_name, contribution_data):
    """Creates a plot that shows the number of contributors to the
    given astropy-affiliated package over time.

    Parameters
    ----------
    package_name : str
        The name of the astropy-affiliated package
    contribution_data : dict
        A dictionary whose keys are usernames and whose values are
        the date in which the user first contributed to the package.
    """

    new_contributors = sorted(contribution_data.values())
    num_contributors = list(range(len(new_contributors)))

    plt.style.use('bmh')
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_title(package_name)
    ax.set_ylabel('# of contributors')

    # Plot the data
    ax.plot(new_contributors, num_contributors)

    # Force x labels to be year only
    years = mdates.YearLocator()
    ax.xaxis.set_major_locator(years)

    plt.savefig(f'plots/{package_name}.png')
    plt.close()


def get_contributor_data(repo_url):
    """Use the GitHub RESTful API to gather contribution data for the
    given repository.

    The data returned from this function includes the contributor
    username and the date in which they first contributed to the
    repository.

    Parameters
    ----------
    repo_url : str
        The url that points to the repository for the astropy-affiliated
        package.

    Returns
    -------
    contribution_data : dict
        A dictionary whose keys are usernames and whose values are
        the date in which the user first contributed to the package.
    """

    # Initialize dict for results
    contributor_data = {}

    # Parse the repo_url for owner and repository name
    owner = repo_url.split('/')[-2]
    repo_name = repo_url.split('/')[-1]

    # Get commit history for the repository
    with open('config.yaml', 'r') as config_file:
        token = yaml.load(config_file)['token']
    headers = {'Authorization': 'token ' + token}
    api_url = f'https://api.github.com/repos/{owner}/{repo_name}/stats/contributors'
    print(f'Gathering data for {repo_name}')
    with requests.get(api_url, headers=headers) as url:
        contributor_history = url.json()

    # Determine when each author's first commit was
    for i, user in enumerate(contributor_history):

        username = user['author']['login']
        contribution_weeks = user['weeks']

        for week in contribution_weeks:
            if week['c'] > 0:
                first_contribution_date = week['w']
                break

        first_contribution_date = datetime.datetime.fromtimestamp(first_contribution_date)
        contributor_data[username] = first_contribution_date

    return contributor_data


def get_package_data():
    """Return a JSON object containing data for astropy-affiliated
    packages, such as repository names and URLs.

    Data is gathered from http://www.astropy.org/affiliated/registry.json

    Returns
    -------
    package_data : obj
        A JSON object containing astropy-affiliated package data.
    """

    with urllib.request.urlopen("http://www.astropy.org/affiliated/registry.json") as url:
        package_data = json.loads(url.read().decode())
        package_data = package_data['packages']

        return package_data


if __name__ == '__main__':

    # Initialize dictionary to hold all of the needed results
    package_contributions = {}

    # Get list of contributors and when they started contributing for
    # each astropy-affiliated package
    package_data = get_package_data()
    for package in package_data:
        package_name = package['name']
        contributor_data = get_contributor_data(package['repo_url'])
        package_contributions[package_name] = contributor_data

        # Create a plot of contributors over time for each package individually
        create_package_plot(package_name, package_contributions[package_name])

    # Create aggregate plot for all packages
    create_aggregate_plot(package_contributions)
