from google.cloud import storage

# define the destination bucket for invalid files

INVALID_FILES_BUCKET = "2mb-bucket"

def check_file_size_and_move(event, context):
    """Triggered by a change to the GCS bucket.
    Args:
        event (dict): The event payload.
        context (google.cloud.functions.Context): The event metadata.
    """
    
    # get the file name and size from the event payload
    source_bucket_name = event['bucket']
    file_name = event['name']
    
    #Initialize GCS client
    storage_client = storage.Client()
    source_bucket = storage_client.bucket(source_bucket_name)
    blob = source_bucket.blob(file_name)

    # Reload the blob to ensure the file size is fetched
    blob.reload()
    
    # Get the file size in bytes
    file_size = blob.size
    
    # Ensure the file size is not None
    if file_size is None:
        print(f"File size is None for {file_name}. skipping...")
        return
    
    max_size = 2 * 1024 * 1024   # 2MB in bytes
     
    if file_size > max_size:
        # Move the file to the "large_files/" folder in the destination bucket
        destination_bucket = storage_client.bucket(INVALID_FILES_BUCKET)
        new_blob_name = f"large_files/{file_name}"  # Add folder prefix
        new_blob = source_bucket.copy_blob(blob, destination_bucket, new_blob_name)
        # Delete the original file
        blob.delete()
        print(f"File size is greater than 2MB for {file_name}. Moved to {INVALID_FILES_BUCKET}/large_files/{file_name} because it exceeded the size limit.")
    else:
        print(f"{file_name} size is within the limit")