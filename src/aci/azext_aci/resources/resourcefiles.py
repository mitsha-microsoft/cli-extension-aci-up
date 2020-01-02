#TODO: Add for ACI Action when created!
#TODO: Container Registry Username and Password are added after querying them. Change this later
DEPLOY_TO_ACI_TEMPLATE = """name: CI
on: [push, pull_request]

jobs:
    build-and-deploy:
        runs-on: ubuntu-latest
        steps:
        - name: 'Checkout GitHub Action'
          uses: actions/checkout@master
        
        - name: 'Login via Azure CLI'
          uses: Azure/docker-login@v1
          with:
              login-server: container_registry_name_place_holder.azurecr.io
              username: container_registry_username
              password: container_registry_password

        - run: |
            docker build . -t container_registry_name_place_holder.azurecr.io/app_name_place_holder:${{ github.sha }}
            docker push container_registry_name_place_holder.azurecr.io/app_name_place_holder:${{ github.sha }}

        - name: 'Azure Login'
          uses: azure/login@v1
          with:
            creds: ${{ secrets.AZURE_CREDENTIALS }}
        
        - name: 'Deploy to Azure Container Instances'
          uses: azure/CLI@v1
          with: 
            azcliversion: 2.0.72
            inlineScript: |
              az container create --resource-group resource_group_place_holder --name app_name_place_holder --image container_registry_name_place_holder.azurecr.io/app_name_place_holder:${{ github.sha }} --ports 80 8080 --dns-name-label app_name_place_holder --registry-username container_registry_username --registry-password container_registry_password""" 

