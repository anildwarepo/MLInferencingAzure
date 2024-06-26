import urllib.request
import json
from azure.servicebus import ServiceBusClient, ServiceBusMessage, AutoLockRenewer
import uuid
import pandas as pd
import threading
import json
import time
from async_inferencing.azureblob_helper import uploadFile
import async_inferencing.load_env
import os

CONNECTION_STR = os.environ["AzureServiceBus_Connection_String"]
TOPIC_NAME = os.environ["Topic_Name"]
SUBSCRIPTION_NAME = os.environ["Subscription_Name"]


session_id = uuid.uuid4()
sender_guid = str(uuid.uuid4())
receiver_guid = str(uuid.uuid4())

def run_with_sync():
    with open('test-data-scoring-async.json') as f:
        data_dict = json.load(f)

    body = str.encode(json.dumps(data_dict))

    url = 'https://ml-inferencing-endpoint-async.northcentralus.inference.ml.azure.com/score'
    # Replace this with the primary/secondary key, AMLToken, or Microsoft Entra ID token for the endpoint
    api_key = os.environ["ML_Endpoint_Apikey"]
    if not api_key:
        raise Exception("A key should be provided to invoke the endpoint")

    # The azureml-model-deployment header will force the request to go to a specific deployment.
    # Remove this header to have the request observe the endpoint traffic rules
    headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key), 'azureml-model-deployment': 'async' }

    req = urllib.request.Request(url, body, headers)

    try:
        response = urllib.request.urlopen(req)

        result = response.read()
        #receive_messages(session_id)
        print(result)
    except urllib.error.HTTPError as error:
        print("The request failed with status code: " + str(error.code))

        # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
        print(error.info())
        print(error.read().decode("utf8", 'ignore'))

def send_messages(session_id: str, message: str):
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR)
    with servicebus_client:
        sender = servicebus_client.get_topic_sender(topic_name=TOPIC_NAME)
        with sender:
            # Create a batch of messages
            messages = [
                #ServiceBusMessage("Message 1", session_id="session1"),
                #ServiceBusMessage("Message 2", session_id="session1"),
                #ServiceBusMessage("Message 3", session_id="session2"),
                ServiceBusMessage(message, session_id=session_id),
            ]
            sender.send_messages(messages)
            print("Messages sent.")

def receive_messages(session_id: str):
    auto_lock_renewer = AutoLockRenewer()
    while True:
        servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR)
        try:
            with servicebus_client:
                receiver = servicebus_client.get_subscription_receiver(
                    topic_name=TOPIC_NAME,
                    subscription_name=ML_ENDPOINT_SUBSCRIPTION_NAME,
                    session_id=session_id
                )
                with receiver:
                    auto_lock_renewer.register(receiver, receiver.session)
                    while True:
                        received_msgs = receiver.receive_messages(max_message_count=10, max_wait_time=5)
                        for msg in received_msgs:
                            print("\nReceived on client: \n" + str(msg))
                            # Complete the message so that it is not received again
                            receiver.complete_message(msg)
        except Exception as e:
            if "lock on the session has expired" in str(e):
                print("Session lock expired. Re-establishing session...")
                time.sleep(5)  # wait for a short period before retrying
            else:
                print("An error occurred: ", str(e))
                break  # Exit the loop if it's an unexpected error

def start_receiving_messages():
    receive_thread = threading.Thread(target=receive_messages, args=(sender_guid,))
    receive_thread.daemon = True
    print(f"Starting to receive messages on client session-id {sender_guid}...")
    receive_thread.start()

def run_with_async():
    data_dict = {}
    while True:
        user_input = input("Press y to send json payload: ")
        #send_messages(sender_guid, user_input)
        #receive_messages(receiver_guid)
        if user_input.lower() == 'y':
            blob_url = uploadFile("./test-data-scoring-async.json")
            data_dict['session_id'] = sender_guid
            data_dict['blob_url'] = blob_url
            send_messages(sender_guid, str.encode(json.dumps(data_dict)))
        else:
            continue


if __name__ == '__main__':
    # parse args
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("op_type", help="async or async")
    args = parser.parse_args()

    if args.op_type == 'sync':
        run_with_sync()
    elif args.op_type == 'async':
        start_receiving_messages()
        run_with_async()

