#TODO: Add for ACI Action when created!
DEPLOY_TO_ACI_TEMPLATE = """name: CI
"on": [push, pull_request]

jobs:
    build-and-deploy:
        runs-on: ubuntu-latest
        steps:
        - name: 'Checkout GitHub Action'
          uses: actions/checkout@v4
        
        - name: 'Login via Azure CLI'
          uses: Azure/docker-login@v2
          with:
              login-server: container_registry_name_place_holder.azurecr.io
              username: ${{ secrets.REGISTRY_USERNAME }}
              password: ${{ secrets.REGISTRY_PASSWORD }}

        - run: |
            docker build . -t container_registry_name_place_holder.azurecr.io/app_name_place_holder:${{ github.sha }}
            docker push container_registry_name_place_holder.azurecr.io/app_name_place_holder:${{ github.sha }}

        - name: 'Azure Login'
          uses: azure/login@v2
          with:
            creds: ${{ secrets.AZURE_CREDENTIALS }}
        
        - name: 'Deploy to Azure Container Instances'
          uses: azure/CLI@v2
          with: 
            azcliversion: latest
            inlineScript: |
              az container create --resource-group resource_name_place_holder --name app_name_place_holder --image container_registry_name_place_holder.azurecr.io/app_name_place_holder:${{ github.sha }} --ports 80 port_number_place_holder --dns-name-label app_name_place_holder --registry-username ${{ secrets.REGISTRY_USERNAME }} --registry-password ${{ secrets.REGISTRY_PASSWORD }}""" 

