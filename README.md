# Azure ACI Extension for Azure CLI
---

The Azure ACI Extension for Azure CLI adds ```az aci up``` Functionality to the Azure CLI.

# Quick Start
1. [Install the Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli)
2. Add the ACI Extension. Go to the releases tab and download the latest release. Then use the command ```az extension add -s '(path-to-whl-file)'``` (Replace path-to-whl-file to the path where you download the whl file).
3. Run the ```az login``` command

# Usage
```$ az aci up --code [link-to-repository]```

# Parameters
```--code```                    : Link to Code Repository (Empty if Current Working Directory Contains the Code).

```--do-not-wait```             : Do not wait for workflow completion. (Default False).

```--port```                   : Port on which your application runs (Default is 8080).

```--skip-secrets-generation``` : Set to True if have stored AZURE_CREDENTIALS & Registry Details Secrets in your Repository (Default False).
