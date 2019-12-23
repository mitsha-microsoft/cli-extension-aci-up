#TODO: Add for ACI Action when created!
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
              username: ${{ secrets.REGISTRY_USERNAME }}
              password: ${{ secrets.REGISTRY_PASSWORD }}

        - run: |
            docker build . -t container_registry_name_place_holder.azurecr.io/app_name_place_holder:${{ github.sha }}
            docker push container_registry_name_place_holder.azurecr.io/app_name_place_holder:${{ github.sha }}

        - uses: azure/webapps-container-deploy@v1
          with:
              app-name: 'app_name_place_holder'
              images: 'container_registry_name_place_holder.azurecr.io/'"""

