from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult, AnalyzeDocumentRequest
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os
import sys

# dotenv
from dotenv import load_dotenv
load_dotenv()

#load environment variables
endpoint = os.getenv("DOCUMENT_ENDPOINT")
key = os.getenv("DOCUMENT_KEY")
def load_pdf_in_storage_account(file_path):
    # Implement the function to load the PDF from the storage account
    # For example, you can use Azure Storage SDK to get the URL of the PDF
    # This is a placeholder implementation
    blob_service_client = BlobServiceClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))
    # Create a container
    container_name = "mydocuments"
    # test if container exists in the blob service client
    try:
        container_client = blob_service_client.get_container_client(container_name)
        container_client.get_container_properties()
    except Exception as e:
        print(f"Container {container_name} does not exist. Creating a new one.")
        blob_service_client.create_container(container_name)


    # Check if the blob exists
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_path)
    try:
        blob_client.get_blob_properties()
        print(f"Blob {file_path} already exists in the container.")
    except Exception as e:
        print(f"Blob {file_path} does not exist in the container. Uploading a new one.")
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data)


    # Generate a public URL
    blob_url = blob_client.url
    print(f"Public URL: {blob_url}")
    return blob_url

docUrl = load_pdf_in_storage_account("data/formulaire-de-demande.pdf")

document_analysis_client = DocumentIntelligenceClient(endpoint=endpoint, 
    credential=AzureKeyCredential(key))

poller = document_analysis_client.begin_analyze_document(
        "prebuilt-layout", AnalyzeDocumentRequest(url_source=docUrl
    ))

AnalyzeResult = poller.result()
print("Analysis completed with result of {}".format(AnalyzeResult.status))
print("Document was analyzed with version {}".format(AnalyzeResult.analyze_result_version))
print("Document has {} pages".format(len(AnalyzeResult.pages)))
print("Document has {} tables".format(len(AnalyzeResult.tables)))
print("Document has {} forms".format(len(AnalyzeResult.forms)))