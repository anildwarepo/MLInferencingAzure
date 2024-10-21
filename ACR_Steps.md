az login
az acr build --registry $ACR_NAME -g container --image mlflowmodelenv:1.0 .