# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger
from knack.util import CLIError
from azext_aci.common.prompting import prompt_user_friendly_choice_list
from azext_aci.common.azure_cli_resources import get_default_subscription_info

logger = get_logger(__name__)

def get_azure_credentials():
    import subprocess
    import json
    subscription_id, subscription_name, tenant_id, _environment_name = get_default_subscription_info()
    azure_creds_user_choice = 1
    print('')
    print('You need to include the following key value pairs as part of your Secrets in the GitHub Repo Setting.')
    while azure_creds_user_choice == 1:
        print('Please go to your GitHub Repo page -> Settings -> Secrets -> Add a new secret and include the following name value pairs.')
        print('')
        print('Name: AZURE_CREDENTIALS')
        auth_details = subprocess.check_output('az ad sp create-for-rbac --sdk-auth -o json', shell=True)
        auth_details_json = json.loads(auth_details)
        print('Value:')
        print(json.dumps(auth_details_json, indent=2))
        print('')
        sp_details = subprocess.check_output('az ad sp create-for-rbac -o json', shell=True)
        sp_details_json = json.loads(sp_details)
        print('Name: REGISTRY_USERNAME')
        print('Value: ',sp_details_json['appId'])
        print('')
        print('Name: REGISTRY_PASSWORD')
        print('Value: ',sp_details_json['password'])
        print('')
        user_choice_list = []
        user_choice_list.append('Yes. Continue')
        user_choice_list.append('No. Re-generate the values for AZURE_CREDENTIALS, REGISTRY_USERNAME and REGISTRY_PASSWORD')
        azure_creds_user_choice = prompt_user_friendly_choice_list('Have you copied the name and value for AZURE_CREDENTIALS, REGISTRY_USERNAME and REGISTRY_PASSWORD:', user_choice_list)
    return