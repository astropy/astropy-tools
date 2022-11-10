"""Checks that are hopefully consistent with APE 18."""
import datetime

import requests
from dateutil.relativedelta import relativedelta
from github import Github
from packaging.version import Version


def get_pkg_pypi_json(package_name):
    url = f'https://pypi.org/pypi/{package_name}/json'
    r = requests.get(url)
    if r.ok:
        return r.json()
    else:
        raise ValueError(r.reason)


def check_ape18_cpython(token=None):
    """All minor versions of Python released 42 months prior to a non-bugfix,
    and at minimum the two latest minor versions.
    """
    utcnow = datetime.datetime.utcnow()
    fourtytwo_mo_ago = utcnow - relativedelta(months=42)

    g = Github(token)
    repo = g.get_repo('python/cpython')
    newest_release_str = ''
    oldest_release_str = ''
    oldest_release_date = None
    cur_major = 0

    # Assume reverse chronological order.
    # This assumes all the tags are of the same major release.
    for tag in repo.get_tags():
        tag_name = tag.name
        tag_date = tag.commit.commit.committer.date
        cur_release = Version(tag_name)
        cur_minor = cur_release.minor
        if (cur_release.dev or cur_release.pre or cur_release.post
                or cur_release.micro != 0):
            continue
        if not newest_release_str:  # Set baseline
            newest_release_str = tag_name
            cur_major = cur_release.major
            two_minor_ago = cur_minor - 2
            print(f'Newest: {newest_release_str}')
            continue
        elif cur_release.major != cur_major:
            continue
        print(f'Processing {tag_name}')  # DEBUG
        if tag_date >= fourtytwo_mo_ago or cur_minor > two_minor_ago:
            oldest_release_str = tag_name
            oldest_release_date = tag_date
        elif tag_date < fourtytwo_mo_ago and oldest_release_str:
            break

    print(f'Oldest to support: {oldest_release_str} ({oldest_release_date})')


def check_ape18_numpy():
    """All minor versions of numpy released in the 24 months prior to a non-bugfix,
    and at minimum the last three minor versions.
    """
    d = get_pkg_pypi_json('numpy')
    last_release_str = d['info']['version']
    last_release = Version(last_release_str)

    # Numpy: At least 3 minor version
    three_minor_ago = last_release.minor - 3
    if three_minor_ago >= 0:
        oldest_release_str = f'{last_release.major}.{three_minor_ago}.0'
    else:
        raise ValueError(f'{last_release_str} has no 3 minor releases ago; '
                         'Help me, human!')

    utcnow = datetime.datetime.utcnow()
    oldest_ts = d['releases'][oldest_release_str][0]['upload_time']
    oldest_release_date = datetime.datetime.strptime(
        oldest_ts, '%Y-%m-%dT%H:%M:%S')
    twentyfour_mo_ago = utcnow - relativedelta(months=24)

    if oldest_release_date <= twentyfour_mo_ago:
        print(f'{oldest_release_str} released on {oldest_ts} is more than '
              '24 months ago')
    else:
        check_ape18_other('numpy', d=d)


# TODO: https://github.com/astropy/astropy-APEs/issues/80
def check_ape18_other(package_name, d=None):
    """Versions of other runtime dependencies released 24 months prior to a
    non-bugfix release.
    """
    if d is None:
        d = get_pkg_pypi_json(package_name)
    last_release_str = d['info']['version']
    last_release = Version(last_release_str)

    utcnow = datetime.datetime.utcnow()
    twentyfour_mo_ago = utcnow - relativedelta(months=24)

    stop = False
    max_iter = 8
    i = 1
    while not stop and i <= max_iter:
        older_minor = last_release.minor - i
        if older_minor < 0:
            raise ValueError(f'{last_release_str} has no {i} minor release(s) '
                             'ago; Help me, human!')
        older_release_str = f'{last_release.major}.{older_minor}.0'
        older_ts = d['releases'][older_release_str][0]['upload_time']
        older_release_date = datetime.datetime.strptime(
            older_ts, '%Y-%m-%dT%H:%M:%S')
        if older_release_date < twentyfour_mo_ago:
            stop = True
        else:
            oldest_release_str = older_release_str
            oldest_ts = older_ts
        i += 1
    print(f'{package_name} minversion should be {oldest_release_str} released '
          f'on {oldest_ts}, the oldest within 24 months')
