import base64
import requests
from knack.prompting import prompt, prompt_pass
from knack.log import get_logger
from knack.util import CLIError
from azext_aci.common.utils import singleton, time_now_as_string

ACI_UP_GITHUB_PAT_ENVKEY = "GITHUB_PAT"
logger = get_logger(__name__)

@singleton
class GithubCredentialManager():
    """
    GithubCredential Manager
    """
    def __init__(self):
        self.username = None
        self.password = None
        self.token = None

    def _create_token(self, token_prefix, note=None):
        #TODO: when a token is created using username and password, it is not stored, neither returned to the user. Thus whenever you reuse this command, you will need to generate new token.
        logger.warning('We need to create a Personal Access Token to communicate with GitHub.'
                        'A new PAT will be created with scopes - admin:repo_hook, repo, user.')
        logger.warning('You can set the PAT in the environment variable (%s) to avoid getting prompted for username and password.', ACI_UP_GITHUB_PAT_ENVKEY)
        print('')
        self.username = prompt(msg='Enter your GitHub Username (Leave Blank to use an already generated PAT): ')
        if not self.username:
            while not self.token:
                self.token = prompt_pass(msg='Enter your GitHub PAT: ', help_string='Generate a Personal Access Token with appropriate permissions from GitHub Developer Settings and paste here.')
            print('')
            return
        self.password = prompt_pass(msg='Enter your GitHub Password: ')
        if not note:
            note = token_prefix + '_AciUpCLIExtension_' + time_now_as_string()
        encoded_pass = base64.b64encode(self.username.encode('utf-8') + b':' + self.password.encode('utf-8'))
        basic_auth = 'basic ' + encoded_pass.decode('utf-8')
        request_body = {
            'scopes': [
                'admin:repo_hook',
                'repo',
                'user'
            ],
            'note': note
        }
        headers = {'Content-Type': 'application/json' + '; charset=utf-8',
                    'Accept':'application/json',
                    'Authorization': basic_auth}
        response = self.post_authorization_request(headers=headers, body=request_body)
        if (response.status_code == 401 and response.headers.get('X-GitHub-OTP') and response.headers.get('X-GitHub-OTP').startswith('required')):
            two_factor_code = None
            while not two_factor_code:
                two_factor_code = prompt_pass(msg='Enter your two factor Authentication code: ')
            print('')
            headers = {'Content-Type': 'application/json' + '; charset=utf-8',
                    'Accept':'application/json',
                    'Authorization': basic_auth,
                    'X-GitHub-OTP': two_factor_code}
            response = self.post_authorization_request(headers=headers, body=request_body)
        import json
        response_json = json.loads(response.content)
        if response.status_code == 200 or response.status_code == 201:
            logger.warning('Created new Personal Access Token with scopes - admin:repo_hook, repo, user.')
            logger.warning('Name: %s',note)
            logger.warning('You can revoke this from your GitHub settings if this pipeline is no longer required.')
            print('')
            self.token = response_json['token']
        else:
            raise CLIError('Could not create a Personal Access Token for GitHub. Check your credentials and try again.')
        return

    def post_authorization_request(self, headers, body):
        return requests.post('https://api.github.com/authorizations', json=body, headers=headers)

    def get_token(self, token_prefix, note=None, display_warning=False):
        import os
        github_pat = os.getenv(ACI_UP_GITHUB_PAT_ENVKEY, None)
        if github_pat:
            if display_warning:
                logger.warning('Using GitHub PAT Token found in Environment Variable (%s).',ACI_UP_GITHUB_PAT_ENVKEY)
                print('')
            return github_pat
        if not self.token:
            self._create_token(token_prefix=token_prefix, note=note)
        return self.token
        