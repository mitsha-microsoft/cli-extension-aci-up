import os
from os.path import dirname, abspath
from knack.log import get_logger
from knack.util import CLIError
from azext_aci.common.git_api_helper import Files
from azext_aci.common.const import (APP_NAME_DEFAULT, APP_NAME_PLACEHOLDER, PORT_NUMBER_PLACEHOLDER, ACR_PLACEHOLDER)

logger = get_logger(__name__)
PACKS_ROOT_STRING = os.path.sep+'resources'+os.path.sep+'packs'+os.path.sep
FILE_ABSOLUTE_PATH = abspath(dirname(abspath(__file__)))

def get_docker_templates(language, port):
    files = []
    language_packs_path = get_supported_language_packs_path(language)
    if language_packs_path:
        docker_file_path = r'Dockerfile'
        file_path = FILE_ABSOLUTE_PATH + language_packs_path + docker_file_path
        file_content = get_file_content(file_path)
        docker_file_content = replace_port(file_content, port)
        docker_file = Files(path=docker_file_path, content=docker_file_content)
        logger.debug("Checkin file path: {}".format(docker_file.path))
        logger.debug("Checkin file content: {}".format(docker_file.content))
        files.append(docker_file)

        docker_ignore_path = r'.dockerignore'
        file_path = FILE_ABSOLUTE_PATH + language_packs_path + docker_ignore_path
        docker_ignore_content = get_file_content(file_path)
        docker_ignore = Files(path=docker_ignore_path, content=docker_ignore_content)
        logger.debug("Checkin file path: {}".format(docker_ignore.path))
        logger.debug("Checkin file content: {}".format(docker_ignore.content))
        files.append(docker_ignore)
    return files


def replace_port(file_content, port):
    content = file_content.replace(PORT_NUMBER_PLACEHOLDER, port)
    return content

def get_file_content(path):
    try:
        filecontent = open(path).read()
        return filecontent
    except Exception as ex:
        raise CLIError(ex)

def get_supported_language_packs_path(language):
    return (PACKS_ROOT_STRING + language.lower() + os.path.sep)

def choose_supported_language(languages):
    #TODO: This is stored here instead of in custom.py to get the packs path string. Check whether works properly or not!
    list_languages = list(languages.keys())
    first_language = list_languages[0]
    abs_packs_path = FILE_ABSOLUTE_PATH + PACKS_ROOT_STRING
    language_packs_list = os.listdir(abs_packs_path)
    if first_language.lower() in language_packs_list:
        return first_language
    elif list_languages[1].lower() in language_packs_list:
        return list_languages[1]
    return None
