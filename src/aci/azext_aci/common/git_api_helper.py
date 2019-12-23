import requests
from knack.log import get_logger
from knack.util import CLIError
# Resolve git ref heads and get branch name from ref

logger = get_logger(__name__)

_HTTP_NOT_FOUND_STATUS = 404
_HHTP_SUCCESS_STATUS = 200
_HTTP_CREATED_STATUS = 201

class Files:
    def __init__(self, path, content):
        self.path = path
        self.content = content

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

def push_files_github(files, repo_name, branch, commit_to_branch, message="Set up CI with Azure Pipelines"):
    if commit_to_branch:
        return commit_files_to_github_branch(files, repo_name, branch, message)

def get_application_json_header():
    return {'Content-Type': 'application/json' + '; charset=utf-8', 'Accept': 'application/json'}

def commit_files_to_github_branch(files, repo_name, branch, message):
    if files:
        for file in files:
            commit_sha = commit_file_to_github_branch(file.path, file.content, repo_name, branch, message)
        return commit_sha
    else:
        raise CLIError('No files to checkin.')

def commit_file_to_github_branch(path_to_commit, content, repo_name, branch, message):
    """
    API Documentation - https://developer.github.com/v3/repos/contents/#create-a-file
    """
    import base64
    headers = get_application_json_header()
    url_for_github_file_api = 'https://api.github.com/repos/{repo_name}/contents/{path_to_commit}'.format(repo_name=repo_name, path_to_commit=path_to_commit)
    if path_to_commit and content:
        path_to_commit = path_to_commit.strip('.')
        path_to_commit = path_to_commit.strip('/')
        encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        request_body = {
            "message": message,
            "branch": branch,
            "content": encoded_content
        }
        token = get_github_pat_token()
        logger.warning('Checking in file %s in the GitHub repository %s', path_to_commit, repo_name)
        response = requests.put(url_for_github_file_api, auth=('', token), json=request_body, headers=headers)
        logger.debug(response.text)
        if not response.status_code == _HTTP_CREATED_STATUS:
            raise CLIError('GitHub file checkin failed for file ({file}), Status code ({code}).'.format(file=path_to_commit, code=response.status_code))
        else:
            commit_obj = response.json()['commit']
            commit_sha = commit_obj['sha']
            return commit_sha
    else:
        raise CLIError('GitHub file checkin failed. File path or content is empty.')



