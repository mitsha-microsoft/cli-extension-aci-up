# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from knack.log import get_logger
from knack.prompting import prompt

from azext_aci.common.git import get_repository_url_from_local_repo, uri_parse
from azext_aci.resources.docker_template import get_docker_file, choose_supported_language
from azext_aci.common.git_api_helper import Files

logger = get_logger(__name__)

def create_aci(cmd, resource_group_name, aci_name, location=None, tags=None):
    raise CLIError('TODO: Implement `aci create`')


def list_aci(cmd, resource_group_name=None):
    raise CLIError('TODO: Implement `aci list`')

def aci_up(code=None):
    """
    Build and Deploy to Azure Container Instances using GitHub Actions
    :param code: URL of the Repository where the code exists
    :type code: str
    """
    #TODO: Implement Az Aci Up
    if code is None:
        code = get_repository_url_from_local_repo()
        logger.debug('GitHub Remote URL Detected from Local Repository is: {}'.format(code))
    if not code:
        raise CLIError('The following arguments are required: --code.')
    repo_name = _get_repo_name_from_repo_url(code)
    
    from azext_aci.common.git_api_helper import get_languages_for_repo, push_files_github
    languages = get_languages_for_repo(repo_name)
    if not languages:
        raise CLIError('Language Detection has Failed in this Repository.')
    elif 'Dockerfile' not in languages.keys():
        docker_file = get_docker_file(languages)
        if docker_file:
            push_files_github(docker_file, repo_name, 'master', True, message='Checking in Dockerfile for Deployment Workflow')
    from azext_aci.common.azure_cli_resources import get_default_subscription_info, get_acr_details
    acr_details = get_acr_details()
    logger.debug(acr_details)
    #TODO: Get the Yaml Workflow file
    files = get_yaml_template_for_repo(languages, acr_details, repo_name)
    logger.warning('Setting up your workflow. This will require 1 or more files to be checked in to the repository.')
    for file_name in files:
        logger.debug("Checkin file path: {}".format(file_name.path))
        logger.debug("Checkin file content: {}".format(file_name.content))
    workflow_commit_sha = push_files_github(files, repo_name, 'master', True, message="Setting up Container Deployment Workflow.")
    print(workflow_commit_sha)
    print('GitHub workflow is setup for continuous deployment.')
    

def _get_repo_name_from_repo_url(repository_url):
    """
    Gives the owner/repository name for GitHub Repos and Repository name for a valid GitHub or Azure Repos URL
    """
    parsed_url = uri_parse(repository_url)
    logger.debug('Parsing GitHub URL: %s',parsed_url)
    if parsed_url.scheme == "https" and parsed_url.netloc == "github.com":
        logger.debug('Parsing Path in the URL to Find the Repo ID.')
        stripped_path = parsed_url.path.strip('/')
        if stripped_path.endswith('.git'):
            stripped_path = stripped_path[:-4]
        return stripped_path
    #TODO: For Azure Repos
    raise CLIError('Could not parse the Repository URL.')

def get_yaml_template_for_repo(languages, acr_details, repo_name):
    language = choose_supported_language(languages)
    if language:
        logger.warning('%s repository detected.', language)
        files_to_return = []
        from azext_aci.resources.resourcefiles import DEPLOY_TO_ACI_TEMPLATE

        files_to_return.append(Files(path='.github/workflows/main.yml', content=DEPLOY_TO_ACI_TEMPLATE
                                                                            .replace(APP_NAME_PLACEHOLDER, APP_NAME_DEFAULT)
                                                                            .replace(ACR_PLACEHOLDER, acr_details['name'])))
        return files_to_return
    else:
        logger.debug('Languages detected: {}'.format(languages))
        raise CLIError('The languages in this repository are not yet supported from the up command.')

def update_aci(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance

ACR_PLACEHOLDER = 'container_registry_name_place_holder'
APP_NAME_PLACEHOLDER = 'app_name_place_holder'
APP_NAME_DEFAULT = 'TestContainerApp'