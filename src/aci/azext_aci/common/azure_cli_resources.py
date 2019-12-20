from knack.log import get_logger
from knack.util import CLIError
from azext_aci.common.prompting import prompt_user_friendly_choice_list

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
        registry_choice = prompt_user_friendly_choice_list("Which Azure Container Registry do you want to use for this pipeline?", registry_choice_list)
        if registry_choice == len(registry_choice_list) + 1:
            return []
        else:
            return acr_list[registry_choice]