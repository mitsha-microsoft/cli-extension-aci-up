import base64
import requests
from knack.prompting import prompt, prompt_pass
from knack.log import get_logger
from knack.util import CLIError

AZ_DEVOPS_GITHUB_PAT_ENVKEY = "GITHUB_PAT"
logger = get_logger(__name__)

class GithubCredentialManager():
    """
    GithubCredential Manager
    """
    def __init__(self):
        self.username = None
        self.password = None
        self.token = None

    def _create_token(self, note=None):
        logger.warning('We need to create a Personal Access Token to communicate with GitHub.'
                        'A new PAT with scopes (admin:repo_hook, repo, user) will be created.')
        logger.warning('You can set the PAT in the environment variable (%s) to avoid getting prompted.', AZ_DEVOPS_GITHUB_PAT_ENVKEY)
        #TODO: Using Username and Password to Get the PAT Token. Taking it from the user for now
        self.token = prompt_pass(msg='Enter your GitHub PAT: ', help_string='Generate a Personal Access Token with appropriate permissions from GitHub Developer Settings and paste here.')
        return

    def get_token(self, note=None):
        import os
        github_pat = os.getenv(AZ_DEVOPS_GITHUB_PAT_ENVKEY, None)
        if github_pat:
            logger.warning('Using GitHub PAT Token found in Environment Variable (%s).',AZ_DEVOPS_GITHUB_PAT_ENVKEY)
            return github_pat
        if not self.token:
            self._create_token(note=note)
        return self.token
        