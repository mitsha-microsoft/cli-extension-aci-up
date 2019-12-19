import requests
from knack.log import get_logger
from knack.util import CLIError
# Resolve git ref heads and get branch name from ref

logger = get_logger(__name__)

_HTTP_NOT_FOUND_STATUS = 404
_HHTP_SUCCESS_STATUS = 200
_HTTP_CREATED_STATUS = 201

def get_languages_for_repo(repo_name):
    """
    API Documentation - https://developer.github.com/v3/repos/#list-languages
    """
    token = get_github_pat_token()
    get_languages_url = 'https://api.github.com/repos/{repo_id}/languages'.format(repo_id=repo_name)
    get_response = requests.get(url=get_languages_url, auth=('', token))
    if not get_response.status_code == _HHTP_SUCCESS_STATUS:
        raise CLIError('Get Languages Failed. Error: ({err})'.format(err=get_response.reason))
    import json
    return json.loads(get_response.text)

def get_github_pat_token():
    from azext_aci.common.github_credential_manager import GithubCredentialManager
    github_manager = GithubCredentialManager()
    return github_manager.get_token()

def push_files_github():
    pass