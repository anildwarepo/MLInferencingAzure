# Asynchronous Machine Learning Inferencing with Azure Service Bus and Azure Machine Learning Endpoints

## Table of Contents
1. [Overview](#overview)
2. [Azure Service Bus Concepts](#azure-service-bus-concepts)
    - [Topics](#topics)
    - [Subscriptions](#subscriptions)
    - [Sessions](#sessions)
3. [Azure Machine Learning Endpoint](#azure-machine-learning-endpoint)
4. [Machine Learning Scoring File](#machine-learning-scoring-file)
5. [End-to-End Workflow](#end-to-end-workflow)

---

## Overview

Asynchronous machine learning inferencing involves using Azure Service Bus and Azure Machine Learning endpoints to handle large-scale data processing in a non-blocking manner. This approach is beneficial for scenarios where immediate responses are not necessary, and processing can be queued and handled as resources become available.


This repository provides a step-by-step guide to setting up an asynchronous inferencing pipeline using Azure Service Bus and Azure Machine Learning endpoints. The key components include:
* Prebuilt machine learning model artifacts. The model is a telco churn prediction model.
* Azure Machine Learning workspace and environment configurations.
* Azure Machine Learning endpoints for synchronous and asynchronous inferencing.
* Prebuilt scoring file for synchronous and asynchronous inferencing. The same does both.

### Reference Architecture

![](./MLEndpointswithAsyncInferencing.drawio.png)


## Azure Service Bus Concepts

Azure Service Bus is a fully managed enterprise message broker with message queues and publish-subscribe topics. It ensures reliable message delivery and decouples the producers from consumers. Here are the key components involved in asynchronous processing:

### Topics

- **Definition**: A topic is used for publishing messages to multiple subscribers.
- **Use Case**: Ideal for scenarios where messages need to be sent to multiple independent receivers.
- **Example**: A message containing the URL of a blob storage file can be published to a topic, allowing multiple machine learning endpoints to subscribe and process the file independently.

### Subscriptions

- **Definition**: A subscription to a topic is a virtual queue that receives copies of messages sent to the topic.
- **Use Case**: Subscriptions enable filtering and routing of messages to specific endpoints.
- **Example**: Different subscriptions can be set up to route messages to various machine learning models based on certain criteria like message content or metadata.

### Sessions

- **Definition**: Sessions are a way to group related messages for ordered processing.
- **Use Case**: Useful for scenarios where the order of message processing is crucial, such as processing transactions in sequence.
- **Example**: A session can ensure that messages related to a particular user or process are handled in the correct order.


## Prerequisites

Before you begin, ensure you have the following installed on your system:

1. **Python 3.10**
   - Download and install Python 3.10 from the official [Python website](https://www.python.org/downloads/release/python-3100/).
   - Verify the installation by running:
     ```sh
     python --version
     ```

2. **Azure Subscription**
   - You need an active Azure subscription. If you don't have one, you can create a free account at [Azure Free Account](https://azure.microsoft.com/en-us/free/).

3. **Azure CLI**
   - Install the Azure CLI by following the instructions on the [Azure CLI Installation](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) page.
   - Verify the installation by running:
     ```sh
     az --version
     ```

4. **Azure Machine Learning CLI v2**
   
    - Install the Azure Machine Learning CLI v2 by following the instructions on the [Azure Machine Learning CLI Installation](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-configure-cli?view=azureml-api-2&tabs=public) page.
   

5. **Windows or Mac OS Terminal**
   - Ensure you have access to the terminal on your operating system.
     - For Windows: You can use Command Prompt, PowerShell, or Windows Terminal.
     - For Mac OS: Use the Terminal application.
   - Verify the terminal access by opening it and running a simple command like:
     ```sh
     echo "Terminal is working"
     ```




## Create Azure Service Bus Namespace

Please see the following this [link for detailed instructions](https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-quickstart-topics-subscriptions-portal) on creating an Azure Service Bus namespace.


## Create Azure Machine Learning Workspace

To set up an Azure Machine Learning Workspace, you can follow the detailed steps provided here: [Create Azure Machine Learning Workspace](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-manage-workspace?view=azureml-api-2&tabs=python).

## Steps to Run Asynchronous Inferencing:

1. **Login to Azure**:
    ```bash
    az login
    ```

2. **Set the desired subscription**:
    ```bash
    az account set --subscription <subscription-id>
    az configure -l -o table
    ```

3. **Configure defaults for the workspace and resource group**:
    ```bash
    az configure --defaults workspace=aml-northcentral group=aml-rg
    ```



## Registering an Azure ML Model

To register a model in Azure Machine Learning, follow these steps:

Update the name, version, and path of the model in the `model.yml` file.

```bash
cd model
az ml model create -f model.yml
```

## Creating Azure ML Environments

Update name and version of the environment in the `env_async.yml` file.

To create environments for Azure Machine Learning, follow these steps:
    
```bash
cd environment
az ml environment create -f env_async.yml
```


## Azure Machine Learning Endpoint

Azure Machine Learning endpoints are used to deploy models and handle inferencing requests. The endpoint can be configured to process incoming requests asynchronously, providing scalable and reliable inferencing capabilities.

### Key Operations

1. **Create Endpoint**:
```
cd async_inferencing
```

Update name in the `endpoint_async.yml` and run the following command:

    ```bash
    az ml online-endpoint create --file endpoint_async.yml 
    ```
2. **Create Deployment**:

Update name, model, model version and environment in the `deployment_async.yml` file.
Rename secrets.rename to secrets.env and update it with required credentials and names. 

    ```bash
    az ml online-deployment create --file deployment_async.yml 
    ```

3. **Update Deployment**:

If the scoring file or environment needs to be updated, run the following command: 

    ```bash
    az ml online-deployment update --file deployment_async.yml
    ```

4. **Update Endpoint Traffic**:

Allocate traffic to the async endpoint with 100% weight.

    ```bash
    az ml online-endpoint update --name ml-inferencing-endpoint-async --traffic "async=100"
    ```

## Machine Learning Scoring File

The scoring file is a script that defines how the model processes input data and produces output. This script is executed by the Azure Machine Learning endpoint to perform inferencing.

This provided scoring file operates in both sync and async modes. The sync mode processes the data immediately, while the async mode downloads the file from remote storage and processes the data and publishes the results to the Azure Service Bus topic.

### Example Structure

1. **Initialization**:
    - Load the model.
    - Set up any necessary resources or configurations.

    ```python
    def init():
        global model
        # Get the path to the deployed model file and load it
        model_dir =os.getenv('AZUREML_MODEL_DIR')
        model_file = os.listdir(model_dir)[0]
        model_path = os.path.join(os.getenv('AZUREML_MODEL_DIR'), model_file)
        model = mlflow.sklearn.load_model(model_path)
    ```

2. **Run Function**:
    ```python
    def run(data):
        input_data = preprocess(data)
        predictions = run_inferencing(data)
        result = postprocess(predictions)
        return result
    ```

3. **Async processing**:
    ```python
    def receive_messages():
    while True:
        servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR)
        session_id = ""
        with servicebus_client:
            receiver = servicebus_client.get_subscription_receiver(
                topic_name=TOPIC_NAME,
                subscription_name=ML_ENDPOINT_CLIENT_SUBSCRIPTION_NAME,
                #session_id=session_id
            )
            with receiver:
                received_msgs = receiver.receive_messages(max_message_count=10, max_wait_time=5)
                for msg in received_msgs:
                    print("Received: " + str(msg))
                    print("-------------------------")
                    #send_messages(session_id, f"Message received on {session_id}:{str(msg)}")
                    # Complete the message so that it is not received again
                    receiver.complete_message(msg)                
                    try:
                        data_dict = json.loads(str(msg))
                        session_id = data_dict['session_id']
                        blob_url = data_dict['blob_url']
                        blob_data = downloadFile(blob_url)['data']
                        print(f"Blob data downloaded.{blob_data}")
                        data=pd.DataFrame(blob_data)
                        print(f"Data loaded into pandas: {data}")
                        predictions = run_inferencing(data)
                        send_messages(session_id, f"Message received on {session_id}:{predictions}")
                        print("Message sent back to client.")
                    except:
                        print("Invalid message received.")
                        pass
    ```

## End-to-End Workflow

### Workflow Steps

1. **Upload Blob**: Upload data to Azure Blob Storage.
2. **Send Blob URL to Service Bus Topic**: Publish a message containing the blob URL to a Service Bus topic.
3. **Endpoint Receives Message**: The Machine Learning endpoint subscribes to the topic and receives the message.
4. **Download and Process Blob**: The endpoint downloads the blob, runs the model, and processes the data.
5. **Send Result to Service Bus Topic**: The result is sent to another Service Bus topic.
6. **Client Receives Result**: The client subscribes to the result topic and receives the processed data.

### Example Test Scripts

- **Synchronous Test**:

Retrieve endpoint url and key from Azure Machine Learning Studio.

![](./mlendpointurlandkey.png)

Update the `endpoint_url` and `endpoint_key` in the `test-ml-endpoint-async.py` file.

- **Synchronous Test**:
    ```bash
    python .\test-ml-endpoint-async.py sync
    ```

- **Expected Result**:
    ```bash
    python .\test-ml-endpoint-async.py sync
    Environment variables loaded from secrets.env
    b'"[false]"'
    ```
- The sync operation returns the predictions immediately through the Rest API.


- **Asynchronous Test**:
    ```bash
    python .\test-ml-endpoint-async.py async
    ```
- **Expected Result**:
    ```bash
        python .\test-ml-endpoint-async.py async
    Environment variables loaded from secrets.env
    Starting to receive messages on client session-id 1476c5fb-5c53-4680-b020-447984417b27...
    Press y to send json payload: y
    File ./test-data-scoring-async.json uploaded to container mlinferencing as blob test-data-scoring-async.json
    Messages sent.

    Received on client:
    {"session_id": "1476c5fb-5c53-4680-b020-447984417b27", "blob_url": "https://anildwaadlsgen2.blob.core.windows.net/mlinferencing/test-data-scoring-async.json"}
    Press y to send json payload:
    Received on client:
    Message received on 1476c5fb-5c53-4680-b020-447984417b27:[False]
    ```
- The async operation returns the prediction asynchronously through the service bus topic.


## Use Non-workspace Azure Container Registry

Managed Online Endpoints can pull images from Non-workspace Azure Container Registry (ACR). To configure your own Azure Container Registry, you need to create a connection to the ACR and grant pull permission to the system-assigned identity of the endpoint.

If ACR has network firewall, the Private Endpoint for ACR should be created in the same VNet as the Azure Machine Learning workspace.

1. create connection to ACR in Azure ML workspace

acr_connection.yml

```yml

name: test_ws_conn_cr
type: container_registry
target: <url_container_registry> # e.g. myregistry.azurecr.io
credentials:
  type: username_password
  username: __TOKEN__
  password: ***
```

```bash
cd environment_customacr
az ml connection create --file ws_acr_connection.yml
```
3. Create new environment with your custom docker image

Update image in the `env.yml` file.

```bash
cd environment_customacr
az ml environment create -f env.yml
```

3. Grant ACR pull permission to the system assigned identity of the endpoint

```bash
ACR_NAME="<YOUR ACR NAME>"
ACR_RESOURCE_GROUP="<ACR RESOURCE GROUP>"
ENDPOINT_NAME="<YOUR ENDPOINT NAME>"
system_identity=`az ml online-endpoint show --name $ENDPOINT_NAME --query "identity.principal_id" -o tsv`
acr_id=`az acr show --name $ACR_NAME -g $ACR_RESOURCE_GROUP  --query "id" -o tsv`
az role assignment create --assignee-object-id $system_identity --assignee-principal-type ServicePrincipal --scope $acr_id --role acrpull
```

4. Update the Environment name in the deployment.yml file.

5. Create deployment

```bash
az ml online-deployment create --file deployment.yml
```


az ml workspace provision-network -g aml-rg -n aml-testws

az ml workspace show -g aml-rg -n aml-testws --query managed_network