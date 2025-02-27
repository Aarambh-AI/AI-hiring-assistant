import os
import asyncio
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from concurrent.futures import ThreadPoolExecutor

# Constants
connection_string = "DefaultEndpointsProtocol=https;AccountName=aibackenda97d;AccountKey=gcGuEE/WLn5EOo26z5vtB4Gxj+tw7eD3ULZEIn+06MSsdZDE9GSk2StpnQeXXClIqwryvVHvhUvC+AStYgks/g==;EndpointSuffix=core.windows.net"  # Azure Storage connection string
container_name = 'resume-files'  # Azure Blob container name
# local_folder_path = r"/Users/shyam/Downloads/foo"  # Local folder containing files
local_folder_path = r"/Users/shyam/Documents/aarambh/Vipany/cvs/Inbox_files_ashwini_Nimmala"
batch_size = 1000  # Upload 100 files at a time (adjust as needed)

# Metadata to be added to each file
org_id = 'org_2ow5pexgsO0avtK5892cjr1yUry'
user_id = 'user_2o3p5auxogLymfD6ZZgwbrWiSjs'

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
            blob_client.upload_blob(data, metadata=metadata, overwrite=True)
        
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

# Function to get the files from a directory within the specified range (min to max)
def get_files_from_directory(folder_path, min_index, max_index):
    files = []
    # Loop through the directory and add files to the list
    for i, file_name in enumerate(os.listdir(folder_path)):
        if min_index <= i < max_index:  # Only add files within the specified range
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):
                files.append((file_path, file_name))
    return files

# Main function to upload files in batches
async def upload_all_files(min_index, max_index):
    # Get files in the specified range (min to max)
    files = get_files_from_directory(local_folder_path, min_index, max_index)
    total_files = len(files)
    print(f"Total files to upload: {total_files}")
    
    # Process files in batches
    total_batches = (total_files + batch_size - 1) // batch_size  # Calculate total number of batches
    for i in range(0, total_files, batch_size):
        batch_files = files[i:i + batch_size]
        print(f"Uploading batch {i//batch_size + 1} of {total_batches}...")
        await upload_files_in_batch(batch_files)

# Run the upload process
if __name__ == '__main__':
    # Specify the range of files to upload (e.g., from file number 50 to 150)
    asyncio.run(upload_all_files(min_index=0, max_index=49235))
