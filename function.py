import os
import logging
from google.cloud import storage
import functions_framework  # pip install functions-framework

INVALID_FILES_BUCKET = os.environ.get("INVALID_FILES_BUCKET", "2mb-bucket")
MAX_SIZE = 2 * 1024 * 1024  # 2 MB

storage_client = storage.Client()

@functions_framework.cloud_event
def check_file_size_and_move(cloud_event):
    data = cloud_event.data or {}
    bucket_name = data.get("bucket")
    file_name = data.get("name")

    if not bucket_name or not file_name:
        logging.warning("Missing bucket or name in event")
        return "Bad event", 200  # don’t trigger retries for malformed events

    source_bucket = storage_client.bucket(bucket_name)
    blob = source_bucket.blob(file_name)
    blob.reload()
    size = blob.size

    if size is None:
        logging.warning(f"Size is None for {file_name}")
        return "No size", 200

    if size > MAX_SIZE:
        dest_bucket = storage_client.bucket(INVALID_FILES_BUCKET)
        new_name = f"large_files/{file_name}"
        source_bucket.copy_blob(blob, dest_bucket, new_name)
        blob.delete()
        logging.info(f"Moved oversize {file_name} to {INVALID_FILES_BUCKET}/{new_name}")
    else:
        logging.info(f"{file_name} is within size limit ({size} bytes)")

    return "OK", 200
