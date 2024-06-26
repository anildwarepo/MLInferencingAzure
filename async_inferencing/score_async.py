import json
import numpy as np
import pandas as pd
import os
from azureml.core.model import Model
import mlflow
from azure.servicebus import ServiceBusClient, ServiceBusMessage, AutoLockRenewer
import threading
import load_env
from azureblob_helper import downloadFile
import os



CONNECTION_STR = os.environ["AzureServiceBus_Connection_String"]
TOPIC_NAME = os.environ["Topic_Name"]
SUBSCRIPTION_NAME = os.environ["Subscription_Name"]
ML_ENDPOINT_CLIENT_SUBSCRIPTION_NAME = os.environ["ML_Endpoint_Client_Subscription_Name"]


response_message = {}

def send_messages(session_id: str, message: str):
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR)
    with servicebus_client:
        sender = servicebus_client.get_topic_sender(topic_name=TOPIC_NAME)
        with sender:
            # Create a batch of messages
            messages = [
                ServiceBusMessage(message, session_id=session_id),
            ]
            sender.send_messages(messages)
            print("Messages sent.")

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

def start_receiving_messages():
    receive_thread = threading.Thread(target=receive_messages, args=())
    receive_thread.daemon = True
    print(f"Starting to receive messages...")
    receive_thread.start()


def run_inferencing(data):
    data["Partner"] = data["Partner"].map({"Yes": True, "No": False})
    data["Dependents"] = data["Dependents"].map({"Yes": True, "No": False})
    data["PhoneService"] = data["PhoneService"].map({"Yes": True, "No": False})
    data["PaperlessBilling"] = data["PaperlessBilling"].map({"Yes": True, "No": False})
    print(data.head(10))
    # Get a prediction from the model
    predictions = model.predict(data)
    return predictions


# Called when the service is loaded
def init():
    global model
    # Get the path to the deployed model file and load it
    model_dir =os.getenv('AZUREML_MODEL_DIR')
    model_file = os.listdir(model_dir)[0]
    model_path = os.path.join(os.getenv('AZUREML_MODEL_DIR'), model_file)
    model = mlflow.sklearn.load_model(model_path)


# Called when a request is received
def run(raw_data):
    try:
        data_dict = json.loads(raw_data)
        data_list = data_dict['data']
        # Get the input data 
        data=pd.DataFrame(data_list)
        predictions = run_inferencing(data)
        #send_messages(session_id, json.dumps(predictions.tolist()))
        #response_message['response'] = "Prediction inferencing is processing..."
        return json.dumps(predictions.tolist())
    except Exception as e:
        error= str(e)
        error = {"error": error}
        return json.dumps(error)


start_receiving_messages()