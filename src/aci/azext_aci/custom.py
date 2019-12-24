# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import subprocess as sb
import json

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
    # files = get_yaml_template_for_repo(languages, acr_details, repo_name)
    # logger.warning('Setting up your workflow. This will require 1 or more files to be checked in to the repository.')
    # for file_name in files:
    #     logger.debug("Checkin file path: {}".format(file_name.path))
    #     logger.debug("Checkin file content: {}".format(file_name.content))
    # workflow_commit_sha = push_files_github(files, repo_name, 'master', True, message="Setting up Container Deployment Workflow.")
    # print(workflow_commit_sha)
    # print('GitHub workflow is setup for continuous deployment.')
    #TODO: Using az acr and etc commands to deploy the container instead of setting up a workflow
    # Getting the Secret Username and Password for the ACRs
    #TODO: Instead of using try/catch, we can use if-else to get the status of admin-enabled (already present in acr details). Then we can directly query username and password
    try:
        credentials = sb.check_output('az acr credential show -n {}'.format(acr_details['name']), shell=True)
    except Exception:
        # If the ACR is not Admin Enabled, credentials are not shown
        logger.warning('Container Registry {} doesn\'t have admin account enabled. Turning it on.')
        sb.check_output('az acr update -n {} --admin-enabled true'.format(acr_details['name']), shell=True)
        credentials = sb.check_output('az acr credential show -n {}'.format(acr_details['name']), shell=True)
    #TODO: Store the username and password in a more secure way?
    credentials = json.loads(credentials)
    ACR_USERNAME = credentials['username']
    ACR_PASSWORD = credentials['passwords'][0]['value']
    #TODO: Using Docker Build instead of ACR Build for Now. Have to check why ACR Build doesn't work properly
    # Building the Image using ACR Build and then Pushing it to ACR (and fetching the code from GitHub)
    #TODO: This just handles the 'Code in GitHub' Flow
    command_for_build = "docker build -t container_registry_name_place_holder.azurecr.io/app_name_place_holder code_repo_place_holder.git"
    try:
        final_command = command_for_build.replace(APP_NAME_PLACEHOLDER, APP_NAME_DEFAULT).replace(ACR_PLACEHOLDER, acr_details['name']).replace(CODE_REPO_PLACEHOLDER, code)
        build_logs = sb.check_output(final_command, shell=True)
        logger.debug(build_logs)
        command_to_login = "docker login {registry_name}.azurecr.io --username {username} --password {password}".format(registry_name=acr_details['name'], username=ACR_USERNAME, password=ACR_PASSWORD)
        logger.debug('Logging in to ACR')
        login_logs = sb.check_output(command_to_login, shell=True)
        command_to_push = "docker push {registry_name}.azurecr.io/{app_name}".format(registry_name=acr_details['name'], app_name=APP_NAME_DEFAULT)
        logger.debug('Pushing Image to ACR')
        push_logs = sb.check_output(command_to_push, shell=True)
        command_to_logout = "docker logout {registry_name}.azurecr.io".format(registry_name=acr_details['name'])
        logout_logs = sb.check_output(command_to_logout, shell=True)
    except Exception as ex:
        raise CLIError(ex)
    print('Container Image Successfully Built.')
    print('Deploying the Container Instance now.')
    #TODO: Have to open port 8080 for now in ACI. What to do about access? Why not port 80 for the container?
    command_for_deploy = 'az container create --resource-group {resource_group} --name {app_name} --image {acr_name}.azurecr.io/{app_name}:latest --ports 80 8080 --dns-name-label {app_name} --registry-username {registry_username} --registry-password {registry_password}'.format(resource_group=acr_details['resourceGroup'], app_name=APP_NAME_DEFAULT, acr_name=acr_details['name'], registry_username=ACR_USERNAME, registry_password=ACR_PASSWORD)
    try:
        deploy_logs = sb.check_output(command_for_deploy, shell=True)
        logger.debug(deploy_logs)
    except Exception as ex:
        raise CLIError(ex)
    print('Container Instance successfully deployed.')
    # Getting the URL of the Deployed Container
    url_query_command = 'az container show --resource-group {resource_group} --name {app_name} --query ipAddress.fqdn'.format(resource_group=acr_details['resourceGroup'], app_name=APP_NAME_DEFAULT)
    app_url = sb.check_output(url_query_command, shell=True)
    print("Here is the URL for your deployed code: ")
    print('http://'+app_url.decode('utf-8').strip('\n').strip('\r').strip('"')+':8080/')
    
      
    

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
CODE_REPO_PLACEHOLDER = 'code_repo_place_holder'
APP_NAME_DEFAULT = 'test-app'