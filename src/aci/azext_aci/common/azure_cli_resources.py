from knack.log import get_logger
from knack.util import CLIError
from azext_aci.common.prompting import prompt_user_friendly_choice_list_with_create, prompt_user_friendly_choice_list

logger = get_logger(__name__)

def get_default_subscription_info():
    from azure.cli.core._profile import Profile
    profile = Profile()
    subscriptions = profile.load_cached_subscriptions(False)
    for subscription in subscriptions:
        if subscription['isDefault']:
            return subscription['id'], subscription['name'], subscription['tenantId'], subscription['environmentName']
    logger.debug('Your account does not have a default Azure subscription. Please run "az login" to setup account.')
    return None, None, None, None

def get_acr_details(name=None):
    import subprocess
    import json
    subscription_id, subscription_name, tenant_id, _environment_name = get_default_subscription_info()
    logger.warning('Using your default Azure Subscription %s for fetching Azure Container Registries.',subscription_name)
    acr_list = subprocess.check_output('az acr list -o json', shell=True)
    acr_list = json.loads(acr_list)
    if acr_list:
        registry_choice = 0
        registry_choice_list = []
        for acr_clusters in acr_list:
            if not name:
                registry_choice_list.append(acr_clusters['name'])
            elif name.lower() == acr_clusters['name'].lower():
                return acr_clusters
        if name is not None:
            raise CLIError('Container Registry with name {} could not be found. Please check using the command "az acr list."'.format(name))
        registry_choice = prompt_user_friendly_choice_list_with_create("Which Azure Container Registry do you want to use for this pipeline?", registry_choice_list)
        if registry_choice >= len(registry_choice_list):
            # Create new ACR selected
            return create_new_acr()
        else:
            return acr_list[registry_choice]

def create_new_acr():
    import subprocess
    import json
    from knack.prompting import prompt
    print('')
    resource_groups = subprocess.check_output('az group list -o json', shell=True)
    resource_groups = json.loads(resource_groups)
    resource_groups_list = []
    if resource_groups:
        for resource_group in resource_groups:
            resource_groups_list.append(resource_group['name'])
    resource_group_choice = prompt_user_friendly_choice_list("Which Resource Group do you want to use for creating the ACR?", resource_groups_list)
    resource_group_name = resource_groups_list[resource_group_choice]
    registry_name = prompt('Enter the name of the Azure Container Registry you want to create: ')
    print('Creating an Azure Container Registry with the name {name} under Resource Group {resource_group} with a Standard SKU.'.format(name=registry_name, resource_group=resource_group_name))
    acr_create_command = 'az acr create -n {acr_name} -g {resource_group} --sku Standard --admin-enabled true'.format(acr_name=registry_name, resource_group=resource_group_name)
    acr_details = subprocess.check_output(acr_create_command, shell=True)
    return json.loads(acr_details)



    
    