import logging
import sys
import requests

module_logger = logging.getLogger("GithubApi." + __name__)


def parse_repos(repos, keys_to_leave=None):
    logger = logging.getLogger("GithubApi." + __name__ + '.' + sys._getframe(  ).f_code.co_name)
    # repos = requests.get('https://api.github.com/user/repos',
    #                      headers={'Authorization': 'token ' + token})
    repos = github.get
    if repos.status_code != 200:
        logger.error(f'Github Api returned status code {repos.status_code}:{repos.json()["message"]}')
        return []
    repos = repos.json()

    if keys_to_leave:
        repos = [
            {
                key: x.get(key, '') for key in keys_to_leave
            }
            for x in repos
        ]
    return repos
