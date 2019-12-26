import os
from knack.log import get_logger
from knack.util import CLIError
from azext_aci.common.git_api_helper import Files

logger = get_logger(__name__)
PACKS_ROOT_STRING = os.path.sep+'packs'+os.path.sep
FILE_ABSOLUTE_PATH = os.path.abspath(os.path.dirname(__file__))

def get_docker_file(languages):
    languages_packs_path = get_supported_languages_packs_path(languages)
    files = []
    if languages_packs_path:
        try:
            abs_pack_path = FILE_ABSOLUTE_PATH + languages_packs_path
            for r, d, f in os.walk(abs_pack_path):
                for file in f:
                    if '__pycache__' not in r and '__init.py__' not in file:
                        file_path = os.path.join(r, file)
                        file_content = open(file_path).read()
                        if file_path.startswith(abs_pack_path):
                            file_path = file_path[len(abs_pack_path):]
                            file_path = file_path.replace('\\','/')
                        file_obj = Files(path=file_path,content=file_content)
                        logger.debug("Checkin file path: {}".format(file_path))
                        logger.debug("Checkin file content: {}".format(file_content))
                        files.append(file_obj)
        except Exception as ex:
            raise CLIError(ex)
    return files

def get_supported_languages_packs_path(languages):
    language = choose_supported_language(languages)
    if language:
        return (PACKS_ROOT_STRING + language.lower() + os.path.sep)

def choose_supported_language(languages):
    list_languages = list(languages.keys())
    first_language = list_languages[0]
    if first_language == 'JavaScript' or first_language == 'Python' or first_language == 'Java':
        return first_language
    elif len(list_languages) >= 1 and ( 'JavaScript' == list_languages[1] or 'Java' == list_languages[1] or 'Python' == list_languages[1]):
        return list_languages[1]
    return None
