from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
import os
import subprocess
import pick

# Acquire a credential object.
credential = DefaultAzureCredential()

# Retrieve subscription ID from azure cli
subscription_id = subprocess.check_output('az account show --query id -o tsv', shell=True).decode().strip()
print("Using default Azure Subscription. Change the Subscription with 'az account set -s <subscriptionId>'")
print("Subscription ID: ", subscription_id)

# Obtain the management object for resources.
resource_client = ResourceManagementClient(credential, subscription_id)

# Retrieve the list of resource groups with Adventure Day Tag present
group_list = resource_client.resource_groups.list(filter="tagName eq 'azd-env-name'")

title = "Select the Azure Adventure Day Agent to connect to: "
options = [group.tags.get("azd-env-name") for group in list(group_list)]
selected_deployment_name = pick.pick(options, title)[0]
selected_group = next(group for group in resource_client.resource_groups.list() if group.tags.get("azd-env-name") == selected_deployment_name)

# Define the environment variables
env_vars = os.environ.copy()
env_vars['AZURE_SUBSCRIPTION_ID'] = subscription_id
env_vars['AZURE_ENV_NAME'] = selected_deployment_name
print("Adventure Day Agent deployment: ", env_vars['AZURE_ENV_NAME'])
env_vars['AZURE_LOCATION'] = selected_group.location
print("Location: ", env_vars['AZURE_LOCATION'])

# Run the subprocess with the specified environment variables
result = subprocess.run(["azd up -e "+selected_deployment_name +" --no-prompt"], env=env_vars, capture_output=False, text=True, shell=True)

#os.system(f"azd up -e {selected_group} --no-prompt")
print(f"Connected to Azure Adventure Day Agent: {selected_deployment_name}")
exit(0)