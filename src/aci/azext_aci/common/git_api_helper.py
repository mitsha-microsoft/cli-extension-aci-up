import requests
import time
from knack.log import get_logger
from knack.util import CLIError
# Resolve git ref heads and get branch name from ref

logger = get_logger(__name__)

_HTTP_NOT_FOUND_STATUS = 404
_HTTP_SUCCESS_STATUS = 200
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
    if not get_response.status_code == _HTTP_SUCCESS_STATUS:
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

def get_application_json_header_for_preview():
    return {'Accept': 'application/vnd.github.antiope-preview+json'}

def get_check_runs_for_commit(repo_name, commit_sha):
    """
    API Documentation - https://developer.github.com/v3/checks/runs/#list-check-runs-for-a-specific-ref
    """
    token = get_github_pat_token()
    headers = get_application_json_header_for_preview()
    #TODO: Why a Sleep Here?
    time.sleep(1)
    get_check_runs_url = 'https://api.github.com/repos/{repo_id}/commits/{ref}/check-runs'.format(repo_id=repo_name, ref=commit_sha)
    get_response = requests.get(url=get_check_runs_url, auth=('',token), headers=headers)
    if not get_response.status_code == _HTTP_SUCCESS_STATUS:
        raise CLIError('Get Check Runs Failed. Error: ({err})'.format(err=get_response.reason))
    import json
    return json.loads(get_response.text)

def get_work_flow_check_runID(repo_name, commit_sha):
    check_run_found = False
    count = 0
    while(not check_run_found or count > 3):
        check_runs_list_response = get_check_runs_for_commit(repo_name, commit_sha)
        if check_runs_list_response and check_runs_list_response['total_count'] > 0:
            # Fetch the GitHub Actions Check Run and its Check Run ID
            check_runs_list = check_runs_list_response['check_runs']
            for check_run in check_runs_list:
                if check_run['app']['slug'] == 'github-actions':
                    check_run_id = check_run['id']
                    check_run_found = True
                    return check_run_id
        time.sleep(5)
        count = count + 1
    raise CLIError("Couldn't find GitHub Actions check run. Please check 'Actions' tab in your GitHub repo.")

def get_check_run_status_and_conclusion(repo_name, check_run_id):
    """
    API Documentation - https://developer.github.com/v3/checks/runs/#get-a-single-check-run
    """
    token = get_github_pat_token()
    headers = get_application_json_header_for_preview()
    get_check_run_url = 'https://api.github.com/repos/{repo_id}/check-runs/{checkID}'.format(repo_id=repo_name, checkID=check_run_id)
    get_response = requests.get(url=get_check_run_url, auth=('', token), headers=headers)
    if not get_response.status_code == _HTTP_SUCCESS_STATUS:
        raise CLIError('Get Check Run Failed. Error: ({err})'.format(err=get_response.reason))
    import json
    #TODO: Avoided 2 time json.loads. Can check which works better
    get_reponse_json = json.loads(get_response.text)
    return get_reponse_json['status'], get_reponse_json['conclusion']

