from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.document import DocumentTranslationClient

from dotenv import load_dotenv
import os
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
# Load environment variables from .env file
load_dotenv()
# Initialize the Document Translation client
local_file_path = "mydoc.pdf"
endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
print(f"Endpoint: {endpoint}")
key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]

translation_client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))

# Initialize BlobServiceClient with Managed Identity
blob_service_client = BlobServiceClient(account_url=os.environ["AZURE_STORAGE_BLOB_ENDPOINT"], credential=DefaultAzureCredential())

source_container = container_client = blob_service_client.get_container_client(container="input")
target_container = container_client = blob_service_client.get_container_client(container="output")
        

with open(local_file_path, "rb") as data:
    source_container.upload_blob(local_file_path,data, overwrite=True)

source_container_sas_url = source_container.url
target_container_sas_url = target_container.url
print(f"Source container SAS URL: {source_container_sas_url}")
print(f"Target container SAS URL: {target_container_sas_url}")
# Create a translation job
poller = translation_client.begin_translation(source_container_sas_url, target_container_sas_url, "en")

# Wait for the translation to complete
result = poller.result()
# Print the translation result
for document in result:
    print(f"Document ID: {document.id}")
    print(f"Status: {document.status}")
    if document.status == "Succeeded":
        print(f"Translated URL: {document.translated_document_url}")
        # Download the translated file
        translated_blob_name = os.path.basename(document.translated_document_url)
        downloaded_file_path = f"downloaded_{translated_blob_name}"
        with open(downloaded_file_path, "wb") as file:
            blob_client = target_container.get_blob_client(translated_blob_name)
            file.write(blob_client.download_blob().readall())
        print(f"Downloaded translated file to: {downloaded_file_path}")

        # Delete the translated file from the container
        blob_client.delete_blob()
        print(f"Deleted translated file from container: {translated_blob_name}")
    else:
        print(f"Error: {document.error.message if document.error else 'Unknown error'}")
