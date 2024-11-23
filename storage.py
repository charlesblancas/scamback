# Imports the Google Cloud client library
import os
from google.cloud import storage

# Instantiates a client
storage_client = storage.Client(project="scamback")

# The name for the new bucket
bucket_name = "scamback-audio"
bucket = storage_client.bucket(bucket_name)


def upload_to_gcs(source_file_name):
    blob_name = os.path.basename(source_file_name)

    # Create a new blob (object) in the bucket
    blob = bucket.blob(blob_name)

    # Upload the file
    blob.upload_from_filename(source_file_name)

    print(f"File {source_file_name} uploaded to {blob_name}.")


def download_from_gcs(blob_name, destination_file_name=None):
    # Get the blob (object) from the bucket
    blob = bucket.blob(blob_name)

    # Download the blob to the local file
    blob.download_to_filename(destination_file_name)

    print(f"Blob {blob_name} downloaded to {destination_file_name}.")


# Example usage
source_file_name = "README.md"

# upload_to_gcs(source_file_name)
download_from_gcs("Juno.mp3", "Juno.mp3")
