# Azure AI Assistant

This project demonstrates how to use the Azure OpenAI Service to create an AI-powered assistant. The assistant is configured to answer questions about pets, specifically cats and dogs, using a vector store and uploaded files as its knowledge base.

## Features

- Create an AI assistant using Azure OpenAI.
- Upload files to a vector store for knowledge base creation.
- Attach files to threads for enhanced context.
- Run threads and retrieve results with status tracking.

## Prerequisites

1. **Azure OpenAI Service**: Ensure you have access to the Azure OpenAI Service.
2. **Environment Variables**: Set the following environment variables in a `.env` file:
   - `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint.
   - `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key.
3. **Python Dependencies**: Install the required Python packages:
   ```bash
   pip install openai python-dotenv
   ```

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd azure-ai-tips/assistant
   ```

2. Create a `.env` file in the `assistant` directory and add your Azure OpenAI credentials:
   ```env
   AZURE_OPENAI_ENDPOINT=<your-endpoint>
   AZURE_OPENAI_API_KEY=<your-api-key>
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Prepare the files for the vector store:
   - Place your files (e.g., `cats.txt`, `dogs.txt`, `pets.pdf`) in the `mydirectory` folder.

## Usage

1. Run the `main.py` script:
   ```bash
   python main.py
   ```

2. The script will:
   - Create an AI assistant named "Financial Analyst Assistant."
   - Upload files to a vector store named "pets."
   - Attach a file to a thread and run the assistant to generate a response.

3. Monitor the logs for status updates and results.

## File Structure

```
/assistant
├── main.py         # Main script for creating and running the assistant
├── Readme.md       # Project documentation
├── requirements.txt # Python dependencies
├── mydirectory     # Directory for input files (e.g., cats.txt, dogs.txt, pets.pdf)
└── .env            # Environment variables (not included in the repository)
```

## Notes

- Ensure the `mydirectory` folder exists and contains the required files before running the script.
- The assistant's instructions and model can be customized in the `main.py` script.

## References

- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)