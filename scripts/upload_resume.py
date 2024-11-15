import os
import asyncio
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from concurrent.futures import ThreadPoolExecutor

# Constants
connection_string = "DefaultEndpointsProtocol=https;AccountName=aibackenda97d;AccountKey=gcGuEE/WLn5EOo26z5vtB4Gxj+tw7eD3ULZEIn+06MSsdZDE9GSk2StpnQeXXClIqwryvVHvhUvC+AStYgks/g==;EndpointSuffix=core.windows.net"  # Azure Storage connection string
container_name = 'resume-files'  # Azure Blob container name
local_folder_path = r"D:\Aarambh\Vipany Global\data\Resumes"  # Local folder containing files
batch_size = 100  # Upload 100 files at a time (adjust as needed)

# Metadata to be added to each file
org_id = 'org_2n9H2WIXunGn1gktx6zq8ZOnKbO'
user_id = 'user_2n9H111Gd3ZMsgRHahYFtCnrudZ'

# Initialize the BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# Get a container client
container_client = blob_service_client.get_container_client(container_name)

# Function to upload a single file
def upload_file(file_path, file_name):
    try:
        # Get the BlobClient for the specific file
        blob_client = container_client.get_blob_client(file_name)
        metadata = {
                "org_id": org_id,
                "user_id": user_id,
            }
        # Open the file and upload it to Blob Storage
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data,metadata=metadata, overwrite=True)
        
        print(f"File '{file_name}' uploaded successfully.")
    except Exception as e:
        print(f"Error uploading '{file_name}': {e}")

# Function to upload files in batches
async def upload_files_in_batch(batch_files):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        
        # For each file in the batch, submit it to the executor for upload
        for file_path, file_name in batch_files:
            futures.append(loop.run_in_executor(executor, upload_file, file_path, file_name))
        
        # Wait for all futures to complete
        await asyncio.gather(*futures)

# Function to get all the files from a directory
def get_files_from_directory(folder_path):
    files = []
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            files.append((file_path, file_name))
    return files

# Main function to upload all files in batches
async def upload_all_files():
    files = get_files_from_directory(local_folder_path)
    total_files = len(files)
    print(f"Total files to upload: {total_files}")
    
    # Process files in batches
    for i in range(0, total_files, batch_size):
        batch_files = files[i:i + batch_size]
        print(f"Uploading batch {i//batch_size + 1} of {len(files)//batch_size + 1}...")
        await upload_files_in_batch(batch_files)

# Run the upload process
if __name__ == '__main__':
    asyncio.run(upload_all_files())
