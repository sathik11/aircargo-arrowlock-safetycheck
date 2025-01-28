##== pip install azure-storage-blob==##

import os
from azure.storage.blob import BlobServiceClient, ContainerClient

# Azure Blob Storage connection string and container name
connection_string = "your_connection_string"
container_name = "your_container_name"

# Initialize the BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_client = blob_service_client.get_container_client(container_name)

# List all blobs in the container
blobs = container_client.list_blobs()

# Find the latest blob based on the uploaded timestamp
latest_blob = None
latest_timestamp = None

for blob in blobs:
    if latest_timestamp is None or blob.last_modified > latest_timestamp:
        latest_blob = blob
        latest_timestamp = blob.last_modified

if latest_blob:
    # Download the latest blob
    blob_client = container_client.get_blob_client(latest_blob.name)
    download_file_path = os.path.join(os.getcwd(), latest_blob.name)

    with open(download_file_path, "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())

    # Print the metadata
    print(f"Downloaded the latest image: {latest_blob.name}")
    print(f"Timestamp: {latest_timestamp}")
else:
    print("No blobs found in the container.")

#===========================MOVE IMAGES TO PROCESSED CONTAINER======================
# Source and destination container names
source_container_name = "source_container"
destination_container_name = "destination_container"
blob_name = "your_blob_name"

# Initialize the BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# Get the source and destination container clients
source_container_client = blob_service_client.get_container_client(source_container_name)
destination_container_client = blob_service_client.get_container_client(destination_container_name)

# Get the source blob client
source_blob_client = source_container_client.get_blob_client(blob_name)

# Get the destination blob client
destination_blob_client = destination_container_client.get_blob_client(blob_name)

# Copy the blob to the new container
copy_source = source_blob_client.url
copy_operation = destination_blob_client.start_copy_from_url(copy_source)

# Wait for the copy operation to complete
properties = destination_blob_client.get_blob_properties()
while properties.copy.status == "pending":
    properties = destination_blob_client.get_blob_properties()

# Check if the copy was successful
if properties.copy.status == "success":
    # Delete the original blob
    source_blob_client.delete_blob()
    print(f"Blob '{blob_name}' moved from '{source_container_name}' to '{destination_container_name}' successfully.")
else:
    print(f"Failed to copy blob '{blob_name}' to '{destination_container_name}'.")

##=============
# pip install pyodbc

import pyodbc
import json

# Azure SQL Database connection details
server = 'your_server.database.windows.net'
database = 'your_database'
username = 'your_username'
password = 'your_password'
driver = '{ODBC Driver 17 for SQL Server}'

# JSON data to be written to the database
json_data = {"CargoLoaded":"Yes",
             "#Locks_Container_Vicinity":"2",
             "#Locks fastened":"2",
             "#Locks unfastened":"0",
             "Safe to lift":"Yes",
             "Confidence_Score":"5"}

# Convert JSON data to string
json_string = json.dumps(json_data)

# Establish a connection to the Azure SQL Database
connection_string = f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}'
conn = pyodbc.connect(connection_string)
cursor = conn.cursor()

# Create a table to store JSON data (if it doesn't exist)
create_table_query = '''
CREATE TABLE IF NOT EXISTS JsonData (
    CargoLoaded INT PRIMARY KEY,
    data NVARCHAR(MAX)
)
'''
cursor.execute(create_table_query)
conn.commit()

# Insert JSON data into the table
insert_query = '''
INSERT INTO JsonData (id, data)
VALUES (?, ?)
'''
cursor.execute(insert_query, json_data['id'], json_string)
conn.commit()

# Close the connection
cursor.close()
conn.close()

print("JSON data written to Azure SQL Database successfully.")
##==========================