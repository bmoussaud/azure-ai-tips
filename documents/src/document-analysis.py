from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient, FormRecognizerClient

import os
import sys

# dotenv
from dotenv import load_dotenv
load_dotenv()

# Store connection information
endpoint = os.getenv("DOCUMENT_ENDPOINT")
key = os.getenv("DOCUMENT_KEY")

fileUri = "https://github.com/MicrosoftLearning/mslearn-ai-document-intelligence/blob/main/Labfiles/01-prebuild-models/sample-invoice/sample-invoice.pdf?raw=true"
fileLocale = "en-US"
fileModelId = "prebuilt-invoice"

print(f"\nConnecting to Forms Recognizer at: {endpoint}")
print(f"Analyzing invoice at: {fileUri}")

# Create the client
document_analysis_client = FormRecognizerClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)

file_path = r"C:\Users\bmoussaud\Workspaces\azure-ai-tips\documents\data\formulaire-de-demande.pdf"
with open(file_path, "rb") as f:        
    form_data = f.read()

print(f"Analyzing invoice at: {file_path}") 

# Analyse the invoice
receipts = document_analysis_client.begin_recognize_invoices(invoice=form_data).result()

# Display invoice information to the user
print("\nInvoice Information:\n")
for idx, receipt in enumerate(receipts.documents):

    customer_name = receipt.fields.get("CustomerName")
    if customer_name:
        print(f"Customer Name: '{customer_name.value}, with confidence {customer_name.confidence}.")


    invoice_total = receipt.fields.get("InvoiceTotal")
    if invoice_total:
        print(f"Invoice Total: '{invoice_total.value.symbol}{invoice_total.value.amount}, with confidence {invoice_total.confidence}.")

print("\nAnalysis complete.\n")