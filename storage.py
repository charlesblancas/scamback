# Imports the Google Cloud client library
import os
from google.cloud import storage

# Instantiates a client
storage_client = storage.Client()

# The name for the new bucket
bucket_name = "scamback-442606"
bucket = storage_client.bucket(bucket_name)


def upload_to_gcs(source_file_name):
    blob_name = os.path.basename(source_file_name)

    # Create a new blob (object) in the bucket
    blob = bucket.blob(blob_name)

    # Upload the file
    blob.upload_from_filename(source_file_name)

    print(f"File {source_file_name} uploaded to {blob_name}.")


# Example usage
source_file_name = "README.md"

upload_to_gcs(source_file_name)
