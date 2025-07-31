# Image Information Extractor

A Python CLI tool that uses Azure OpenAI GPT-4 Vision to extract detailed information from images.

## Features

- Extract comprehensive information from images using GPT-4 Vision
- Support for custom prompts
- Automatic image optimization (resizing, format conversion)
- JSON output support
- Token usage tracking
- Azure credential authentication support

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Azure OpenAI:**
   
   Copy the environment template:
   ```bash
   cp .env.template .env
   ```
   
   Edit `.env` and set your Azure OpenAI endpoint:
   ```
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   ```
   
   Optional configurations:
   - `AZURE_OPENAI_API_KEY`: Your API key (if not using Azure credential)
   - `AZURE_OPENAI_DEPLOYMENT_NAME`: Model deployment name (defaults to extimage-gpt-4.1-mini)
   - `AZURE_OPENAI_API_VERSION`: API version (defaults to 2024-02-01)

3. **Verify setup:**
   ```bash
   python image_analyzer.py setup
   ```

## Usage

### Basic Analysis
```bash
python image_analyzer.py analyze path/to/your/image.jpg
```

### Custom Prompt
```bash
python image_analyzer.py analyze image.jpg --prompt "Extract all text from this image"
```

### Save Results to JSON
```bash
python image_analyzer.py analyze image.jpg --output results.json
```

### Verbose Output
```bash
python image_analyzer.py analyze image.jpg --verbose
```

### All Options
```bash
python image_analyzer.py analyze image.jpg \
  --prompt "Describe the technical components in this diagram" \
  --max-tokens 3000 \
  --output analysis.json \
  --verbose
```

## Examples

### Extract Text from Documents
```bash
python image_analyzer.py analyze document.jpg \
  --prompt "Extract all text content from this document, maintaining the original structure and formatting"
```

### Analyze Charts/Graphs
```bash
python image_analyzer.py analyze chart.png \
  --prompt "Analyze this chart. Describe the data trends, key insights, and any notable patterns"
```

### Identify Objects
```bash
python image_analyzer.py analyze photo.jpg \
  --prompt "List and count all objects visible in this image, categorized by type"
```

## Supported Image Formats

- JPEG/JPG
- PNG
- WebP
- BMP
- TIFF

Images are automatically optimized for API compatibility:
- Resized to maximum 2048x2048 pixels
- Converted to JPEG format
- Quality optimized to 85%

## Authentication

The tool supports two authentication methods:

1. **Azure Default Credential** (Recommended for production):
   - Uses Azure CLI login, managed identity, or service principal
   - No API key needed in environment variables

2. **API Key**:
   - Set `AZURE_OPENAI_API_KEY` in your `.env` file
   - Direct API key authentication

## Output Format

Results are returned in JSON format with the following structure:

```json
{
  "success": true,
  "analysis": "Detailed image analysis text...",
  "usage": {
    "prompt_tokens": 123,
    "completion_tokens": 456,
    "total_tokens": 579
  },
  "model": "extimage-gpt-4.1-mini",
  "image_path": "path/to/image.jpg"
}
```

## Error Handling

The tool includes comprehensive error handling for:
- Missing or invalid image files
- Network connectivity issues
- Authentication problems
- API rate limits and quotas
- Invalid configuration

## License

This project is part of the azure-ai-tips repository.
