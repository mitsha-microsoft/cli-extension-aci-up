from knack.log import get_logger

try:
    from urllib.parse import urlparse, quote
except ImportError:
  from urllib import quote
  from urlparse import urlparse  

logger = get_logger(__name__)

_git_remotes = {}
_ORIGIN_PUSH_KEY = 'origin(push)'
_GIT_EXE = 'git'

def get_repository_url_from_local_repo():
    return get_remote_url(is_github_url_candidate)

def is_github_url_candidate(url):
    if url is None:
        return False
    components = uri_parse(url.lower())
    if components.netloc == "github.com":
        return True
    return False

def uri_parse(url):
    return urlparse(url)

def get_remote_url(validation_function=None):
    remotes = get_git_remotes()
    if remotes is not None:
        if _ORIGIN_PUSH_KEY in remotes and (validation_function is None or validation_function(remotes[_ORIGIN_PUSH_KEY])):
            return remotes[_ORIGIN_PUSH_KEY]
        for k,value in remotes.items():
            if k != _ORIGIN_PUSH_KEY and k.endswith('(push)') and (validation_function is None or validation_function(value)):
                return value
    return None

def get_git_remotes():
    import subprocess
    import sys
    if _git_remotes:
        return _git_remotes
    try:
        # Example output:
        # git remote - v
        # full  https://mseng.visualstudio.com/DefaultCollection/VSOnline/_git/_full/VSO (fetch)
        # full  https://mseng.visualstudio.com/DefaultCollection/VSOnline/_git/_full/VSO (push)
        # origin  https://mseng.visualstudio.com/defaultcollection/VSOnline/_git/VSO (fetch)
        # origin  https://mseng.visualstudio.com/defaultcollection/VSOnline/_git/VSO (push)
        output = subprocess.check_output([_GIT_EXE, 'remote', '-v'], stderr=subprocess.STDOUT)
    except BaseException as ex:
        logger.info('GitDetect: Could not detect current remotes based on current working directory.')
        logger.debug(ex, exc_info=True)
        return None
    if sys.stdout.encoding is not None:
        lines = output.decode(sys.stdout.encoding).split('\n')
    else:
        lines = output.decode().split('\n')
    for line in lines:
        components = line.strip().split()
        if len(components) == 3:
            _git_remotes[components[0] + components[2]] = components[1]
    return _git_remotes

        
