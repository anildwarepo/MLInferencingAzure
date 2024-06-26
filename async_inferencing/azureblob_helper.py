from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import json
import os


connection_string = os.environ["AzureBlobStorage_Connection_String"]
container_name = os.environ["mlinferencing"]
blob_name = os.environ["Blob_Name"]

def uploadFile(filePath):
    # Define your connection string, container name, and blob name

    #file_path = "./test-data-scoring-async.json"

    # Create a BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Create a container client
    container_client = blob_service_client.get_container_client(container_name)

    # Upload the file
    with open(filePath, "rb") as data:
        container_client.upload_blob(name=blob_name, data=data, overwrite=True)

    print(f"File {filePath} uploaded to container {container_name} as blob {blob_name}")
    blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{blob_name}"
    return blob_url




def downloadFile(filePath):
    # Define your connection string, container name, and blob name

    #file_path = "./test-data-scoring-async.json"

    # Create a BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Create a container client
    container_client = blob_service_client.get_container_client(container_name)
   
    blob_data = container_client.download_blob(blob_name).readall()

    blob_content = blob_data.decode('utf-8')

    # Load the string as JSON
    json_data = json.loads(blob_content)

    # Print the JSON data
    #print(json.dumps(json_data, indent=4))
    return json_data

    #print(f"Blob {blob_name} downloaded to {filePath}")

#uploadFile("./test-data-scoring-async.json")


#downloadFile("./test-data-scoring-async-downloaded.json")