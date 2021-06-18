import netrc
import getpass
import warnings

GITHUB_API_HOST = 'api.github.com'

BRANCHES_DICT = {'astropy/astropy': ['v0.1.x', 'v0.2.x', 'v0.3.x', 'v0.4.x',
                                     'v1.0.x', 'v1.1.x', 'v1.2.x', 'v1.3.x',
                                     'v2.0.x',
                                     'v3.0.x', 'v3.1.x', 'v3.2.x',
                                     'v4.0.x', 'v4.1.x', 'v4.2.x', 'v4.3.x'],
                 'astropy/astropy-helpers': ['v0.4.x', 'v1.0.x', 'v1.1.x',
                                             'v1.2.x', 'v1.3.x',
                                             'v2.0.x',
                                             'v3.0.x', 'v3.1.x', 'v3.2.x',
                                             'v4.0.x'],
                 'astropy/astroquery': [],  # we don't have bugfix branches
}


def get_credentials(username=None, password=None, needs_token=False):
    pwtype = 'personal access token' if needs_token else 'password'

    try:
        my_netrc = netrc.netrc()
    except Exception:
        pass
    else:
        auth = my_netrc.authenticators(GITHUB_API_HOST)
        if auth:
            response = 'NONE'  # to allow enter to be default Y
            while response.lower() not in ('y', 'n', ''):
                print('Using the following GitHub credentials from '
                      '~/.netrc: {0}/{1}'.format(auth[0], '*' * 8))
                response = input(
                    'Use these credentials (if not you will be prompted '
                    'for new credentials)? [Y/n] ')
            if response.lower() == 'y' or response == '':
                username = auth[0]
                password = auth[2]
                if needs_token:
                    warnings.warn('Interpreting "password" in netrc as a personal access token')

    if not (username or password):
        print(f"Enter your GitHub username and {pwtype} so that API "
               "requests aren't as severely rate-limited...")
        username = input('Username: ')
        password = getpass.getpass('Password: ')
    elif not password:
        print(f"Enter your GitHub {pwtype} so that API "
               "requests aren't as severely rate-limited...")
        password = getpass.getpass('Password: ')

    return username, password


def get_branches(repo):
    try:
        branches = BRANCHES_DICT[repo]
    except KeyError:
        print("No branches of interest was defined, using all branches with "
              "names starting with a number or v[0-9] ")

        from github import Github
        from common import get_credentials
        g = Github(*get_credentials())
        repo = g.get_repo(repo)

        branches = []

        for br in repo.get_branches():
            if (br.name[0] in '1234567890'
                    or br.name[0] == 'v' and br.name[1] in '1234567890'):
                branches.append(br.name)

    return branches
