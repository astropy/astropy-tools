import netrc
import getpass

GITHUB_API_HOST = 'api.github.com'


def get_credentials(username=None, password=None):

    try:
        my_netrc = netrc.netrc()
    except:
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

    if not (username or password):
        print("Enter your GitHub username and password so that API "
              "requests aren't as severely rate-limited...")
        username = input('Username: ')
        password = getpass.getpass('Password: ')
    elif not password:
        print("Enter your GitHub password so that API "
              "requests aren't as severely rate-limited...")
        password = getpass.getpass('Password: ')

    return username, password
