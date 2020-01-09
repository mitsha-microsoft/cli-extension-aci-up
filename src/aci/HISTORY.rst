.. :changelog:

Release History
===============

0.0.1
++++++
* Initial release. Set's up the GitHub Actions Workflow. User is expected to set the ```AZURE_CREDENTIALS``` secrets in their repository. 
* Uses azure/CLI@v1 GitHub Action to deploy to Azure Container Instances.
* Option to create your own ACR doesn't work.

0.0.2
++++++
* ACR Creation Option works now. Smarter Fetching of App's URL added.
* User can specify their existing ACR using the --acr option.
* Option to generate (or not generate) secrets for ```AZURE_CREDENTIALS``` and ```REGISTRY_USERNAME``` & ```REGISTRY_PASSWORD```
* Option to have a Custom Port for the App Added
* Option to not wait for Workflow Completion Added
* Uses azure/CLI@v1 GitHub Action to deploy to Azure Container Instances.

