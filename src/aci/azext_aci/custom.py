# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import subprocess as sb
from knack.util import CLIError
from knack.log import get_logger
from knack.prompting import prompt

from azext_aci.common.git import get_repository_url_from_local_repo, uri_parse
from azext_aci.common.git_api_helper import Files, get_work_flow_check_runID, get_check_run_status_and_conclusion, get_github_pat_token
from azext_aci.common.github_azure_secrets import get_azure_credentials
from azext_aci.common.const import ( APP_NAME_DEFAULT, APP_NAME_PLACEHOLDER, ACR_PLACEHOLDER, RG_PLACEHOLDER, PORT_NUMBER_DEFAULT, 
                                     RELEASE_PLACEHOLDER, RELEASE_NAME, CONTAINER_REGISTRY_PASSWORD, CONTAINER_REGISTRY_USERNAME )
from azext_aci.docker_template import get_docker_templates, choose_supported_language

logger = get_logger(__name__)

def create_aci(cmd, resource_group_name, aci_name, location=None, tags=None):
    raise CLIError('TODO: Implement `aci create`')


def list_aci(cmd, resource_group_name=None):
    raise CLIError('TODO: Implement `aci list`')

def aci_up(code=None, port=None, skip_secrets_generation=False, do_not_wait=False):
    """
    Build and Deploy to Azure Container Instances using GitHub Actions
    :param code: URL of the Repository where the code exists
    :type code: str
    :param port: Port on which your application runs. Default is 8080
    :type port: int
    :param skip_secrets_generation: Flag to skip generating Azure Credentials
    :type skip_secrets_generation: bool
    :param do_not_wait: Do not wait for workflow completion
    :type do_not_wait: bool
    """
    #TODO: Secrets Generation and Port Selection Options too!
    if code is None:
        code = get_repository_url_from_local_repo()
        logger.debug('GitHub Remote URL Detected from Local Repository is: {}'.format(code))
    if not code:
        code = prompt('GitHub Repository URL (e.g. https://github.com/contoso/webapp/): ')
    if not code:
        raise CLIError('The following arguments are required: --code.')
    repo_name = _get_repo_name_from_repo_url(code)
    
    from azext_aci.common.git_api_helper import get_languages_for_repo, push_files_github
    get_github_pat_token(repo_name, display_warning=True)
    logger.warning('Setting up your workflow.')

    languages = get_languages_for_repo(repo_name)
    if not languages:
        raise CLIError('Language Detection has Failed in this Repository.')

    language = choose_supported_language(languages)
    if language:
        logger.warning('%s repository detected.', language)
    else:
        logger.debug('Languages detected: {}'.format(languages))
        raise CLIError('The languages in this repository are not yet supported from up command.')

    from azext_aci.common.azure_cli_resources import (get_default_subscription_info, get_acr_details)
    acr_details = get_acr_details()
    logger.debug(acr_details)
    print('')

    if port is None:
        port = PORT_NUMBER_DEFAULT
    if 'Dockerfile' not in languages.keys():
        docker_files = get_docker_templates(language, port)
        if docker_files:
            push_files_github(docker_files, repo_name, 'master', True, message='Checking in Dockerfile for Container Deployment Workflow')
    else:
        logger.warning('Using the Dockerfile found in the repository {}'.format(repo_name))

    if not skip_secrets_generation:
        get_azure_credentials()
    
    print('')
    files = get_yaml_template_for_repo(language, acr_details, repo_name)
    logger.warning('Setting up your workflow. This will require 1 or more files to be checked in to the repository.')
    for file_name in files:
        logger.debug("Checkin file path: {}".format(file_name.path))
        logger.debug("Checkin file content: {}".format(file_name.content))
    workflow_commit_sha = push_files_github(files, repo_name, 'master', True, message="Setting up Container Deployment Workflow.")
    print('')
    print('GitHub workflow is setup for continuous deployment.')
    check_run_id = get_work_flow_check_runID(repo_name, workflow_commit_sha)
    workflow_url = 'https://github.com/{repo_id}/runs/{checkID}'.format(repo_id=repo_name, checkID=check_run_id)
    print('For more details, check {}'.format(workflow_url))
    #TODO: Add the option of Do Not Wait. Polling Workflow Status for now!
    poll_workflow_status(repo_name, check_run_id, acr_details)
    

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

def get_yaml_template_for_repo(language, acr_details, repo_name):
    #TODO: ACR Credentials were fetched here. Now done using SP
    files_to_return = []
    from azext_aci.resources.resourcefiles import DEPLOY_TO_ACI_TEMPLATE
    files_to_return.append(Files(path='.github/workflows/main.yml',
        content=DEPLOY_TO_ACI_TEMPLATE
            .replace(APP_NAME_PLACEHOLDER, APP_NAME_DEFAULT)
            .replace(ACR_PLACEHOLDER, acr_details['name'])
            .replace(RELEASE_PLACEHOLDER, RELEASE_NAME)
            .replace(RG_PLACEHOLDER, acr_details['resourceGroup'])))
    return files_to_return

def poll_workflow_status(repo_name, check_run_id, acr_details):
    #TODO: ACR Details passed to get the Resource Group to get the FQDN of the Container. Any other ways?
    import colorama
    import humanfriendly
    import time
    check_run_status = None
    check_run_status, check_run_conclusion = get_check_run_status_and_conclusion(repo_name, check_run_id)
    if check_run_status == 'queued':
        colorama.init()
        with humanfriendly.Spinner(label='Workflow is in queue') as spinner:
            while True:
                spinner.step()
                time.sleep(0.5)
                check_run_status, check_run_conclusion = get_check_run_status_and_conclusion(repo_name, check_run_id)
                if check_run_status == 'in_progress' or check_run_status == 'completed':
                    break
        colorama.deinit()
    if check_run_status == 'in_progress':
        colorama.init()
        with humanfriendly.Spinner(label="Workflow is in Progress") as spinner:
            while True:
                spinner.step()
                time.sleep(0.5)
                check_run_status, check_run_conclusion = get_check_run_status_and_conclusion(repo_name, check_run_id)
                if check_run_status == 'completed':
                    break
        colorama.deinit()
    print('GitHub Workflow Completed.')
    print('')
    if check_run_conclusion == 'success':
        print('Workflow Succeded.')
        resource_group = acr_details['resourceGroup']
        url_find_command = 'az container show --name {app_name} --resource-group {resource_group_name} --query ipAddress.fqdn'.format(app_name=APP_NAME_DEFAULT, resource_group_name=resource_group)
        url_result = sb.check_output(url_find_command, shell=True)
        app_url = "http://"+url_result.decode().strip()+":8080/"
        print('You can see your deployed app at: {}'.format(app_url))
    else:
        raise CLIError('Workflow status: {}'.format(check_run_conclusion))

def update_aci(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance

APP_NAME_DEFAULT = 'test-app'
ACR_USERNAME = ''
ACR_PASSWORD = ''