
Create Azure Service Bus Namespace

https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-quickstart-topics-subscriptions-portal



Create Azure Machine Learning Workspace

https://learn.microsoft.com/en-us/azure/machine-learning/how-to-manage-workspace?view=azureml-api-2&tabs=python

az login


az account set --subscription <subscription-id>
 az configure -l -o table

az ml -h




az configure --defaults workspace=aml-northcentral resource_group=aml-rg
az configure --defaults workspace=aml-northcentral group=aml-rg

az ml workspace set -g aml-rg -w aml-northcentral

az ml model create -f model.yml
az ml model update -f model.yml

az ml model register --name ml-inferening-base-model --version 1 --type MLFLOW --path ./model_artifacts

cd environment
az ml environment create -f env.yml
az ml environment create -f env_async.yml


cd inferencing

az ml online-endpoint create --file endpoint.yml 
az ml online-deployment create --file deployment_production.yml 


az ml online-endpoint create --file endpoint_async.yml 
az ml online-deployment create --file deployment_async.yml 

az ml online-endpoint update --name ml-inferencing-endpoint --traffic "production=100"



upload blob and send blob url to service bus topic
ml endpoint received message, downloads blob, runs model, sends result to service bus topic
client receives result from service bus topic


python .\test-ml-endpoint-async.py sync 


python .\test-ml-endpoint-async.py async 