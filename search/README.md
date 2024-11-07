# Azure AI Tips: Search

This repository contains a PowerShell script to set up Azure resources for a search service.

## Prerequisites

- Azure CLI installed
- PowerShell installed
- An Azure account with appropriate permissions

## load_search_ai.ps1

This PowerShell script is designed to automate the setup and configuration of various Azure resources, including Azure Storage, Azure Cognitive Search, and Azure OpenAI services. It begins by defining several variables, such as the Azure region ($AZURE_REGION), a prefix for naming resources ($prefix), and the resource group name ($RG). Unique names for the storage account, search service, and AI resource are generated using the prefix combined with random numbers to ensure uniqueness.

The script then proceeds to create an Azure Storage account in the specified resource group and region using the az storage account create command. Following this, a storage container named "brochures" is created within the storage account. The script also uploads all PDF files from a specified local directory to this container, ensuring that any existing files with the same names are overwritten.

Next, the script creates an Azure Cognitive Search service with a system-assigned managed identity, using the az search service create command. Similarly, an Azure OpenAI service instance is created with a system-assigned managed identity using the az cognitiveservices account create command. Although there is a commented-out section for deploying a GPT-4.0 model, it indicates that deploying the model using the Azure CLI is not currently functional.

The script then configures managed identities to allow the Azure AI Search and Azure OpenAI instances to access the Azure Blob Storage account. It retrieves the principal IDs of the managed identities for both the search service and the AI resource, as well as the storage account's scope. These identities are then assigned the "Storage Blob Data Contributor" role to grant them the necessary permissions.

Further, the script configures the managed identity for the Azure AI Search instance to access the Azure OpenAI Service instance by assigning the "Cognitive Services OpenAI Contributor" role. Conversely, it also configures the managed identity for the Azure OpenAI Service instance to access the Azure AI Search instance by assigning several roles, including "Search Index Data Contributor," "Search Index Data Reader," and "Search Service Contributor."

Overall, this script automates the creation and configuration of Azure resources and their respective permissions, streamlining the process of setting up an integrated environment for storage, search, and AI services.
    



