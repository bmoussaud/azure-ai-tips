# Translator Example

This repository contains an example of using Azure AI Translator to translate text between different languages. The example demonstrates how to integrate Azure Translator into your application.

## Prerequisites

1. An active [Azure account](https://azure.microsoft.com/free/).
2. An Azure Translator resource. You can create one in the [Azure Portal](https://portal.azure.com/).
3. Node.js or Python installed on your machine (depending on the example you want to run).

## Setup

1. Clone this repository:
    ```bash
    git clone https://github.com/your-repo/azure-ai-tips.git
    cd azure-ai-tips/translation
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Configure infrastructure
    ```
    azd up
    ```

## Usage

Run the translator script:
```bash
azd env get-values > .env
python app.py mydoc.pdf
```

Ouput looks like:
```bash
Local file path: mydoc.pdf
Endpoint: https://dakfqdo5vbzlg.cognitiveservices.azure.com/
Source container SAS URL: https://yi2fmucycxxqy.blob.core.windows.net/input
Target container SAS URL: https://yi2fmucycxxqy.blob.core.windows.net/output
Starting translation job (target language is English) ...
Waiting for translation to complete...
Document ID: 017bbacd-0000-0000-0000-000000000000
Status: Status.SUCCEEDED
Translated URL: https://yi2fmucycxxqy.blob.core.windows.net:443/output/mydoc.pdf
Downloaded translated file to: downloaded_mydoc.pdf
Deleted translated file from container: mydoc.pdf
Deleting input file from container: mydoc.pdf
```

Open the file `downloaded_mydoc.pdf`

Clean up: 

```bash
azd down
```

## Features

- Translate text between multiple languages.
- Detect the source language automatically.
- Support for multiple input formats.

## Resources

- [Azure Translator Documentation](https://learn.microsoft.com/azure/cognitive-services/translator/)
- [Azure SDK for Python](https://github.com/Azure/azure-sdk-for-python)

## License

This project is licensed under the MIT License. See the [LICENSE](../LICENSE) file for details.