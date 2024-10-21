az configure --defaults workspace=airlift-demo-amlws group=airlift-demo-2-aml

az configure --defaults workspace=aml-northcentral group=aml-rg

az configure --defaults workspace=aml-testws group=aml-rg

enable admin user on ACR

run docker desktop locally

az acr login -n crairliftuprp --expose-token

ACR_NAME=crairliftuprp
RESOURCE_GROUP=airlift-demo-2-aml
az acr build --registry $ACR_NAME -g $RESOURCE_GROUP --image mlflowmodelenv:1.0 .




docker build -t  mlflowmodelenv:1.0 .
docker tag mlflowmodelenv:1.0 crairliftuprp.azurecr.io/mlflowmodelenv:1.0
docker push crairliftuprp.azurecr.io/mlflowmodelenv:1.0