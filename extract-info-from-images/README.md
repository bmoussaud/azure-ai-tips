# Image Information Extraction Tools

This folder contains two powerful Python CLI tools for extracting information from images using Azure AI services:

1. **`image_analyzer.py`** - Azure OpenAI GPT-4 Vision direct API tool
2. **`foundry_image_agent.py`** - AI Foundry Agent with Bing grounding for enhanced research ⭐ **NEW**

## 🚀 AI Foundry Agent (Recommended)

The **`foundry_image_agent.py`** is an advanced agent that combines image analysis with web research using AI Foundry SDK and Bing grounding. It extracts names, locations, and tags from images, then automatically researches additional information to create comprehensive markdown reports with external links.

### Features

- **Intelligent Image Analysis**: Extract names, locations, tags, and context from images
- **Automatic Web Research**: Uses Bing grounding to fetch additional information about identified elements
- **Markdown Reports**: Generates comprehensive reports with external links and citations
- **Batch Processing**: Analyze multiple images in a folder with individual reports
- **Azure Integration**: Uses AI Foundry SDK with Azure credential support

### Setup for AI Foundry Agent

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure AI Foundry:**
   
   Copy the environment template:
   ```bash
   cp .env.template .env
   ```
   
   Edit `.env` and set your AI Foundry configuration:
   ```
   # Required
   AZURE_AI_PROJECT_ENDPOINT=https://your-project.cognitiveservices.azure.com/
   BING_CONNECTION_ID=/subscriptions/.../connections/your-bing-connection
   
   # Optional
   MODEL_DEPLOYMENT_NAME=gpt-4o
   AZURE_AI_PROJECT_API_KEY=your-key  # if not using Azure credentials
   ```

3. **Verify setup:**
   ```bash
   python foundry_image_agent.py setup
   ```

### Usage Examples

#### Single Image Analysis with Research
```bash
# Basic analysis with automatic research
python foundry_image_agent.py analyze photo.jpg

# Custom prompt with research
python foundry_image_agent.py analyze photo.jpg --prompt "Focus on architectural elements and historical context"

# Save to specific output file
python foundry_image_agent.py analyze photo.jpg --output my_analysis.md

# Verbose output with details
python foundry_image_agent.py analyze photo.jpg --verbose
```

#### Batch Analysis
```bash
# Analyze all images in a folder
python foundry_image_agent.py analyze-batch ./photos/

# Custom output directory
python foundry_image_agent.py analyze-batch ./photos/ --output-dir ./reports/

# Limit number of images and specific extensions
python foundry_image_agent.py analyze-batch ./photos/ --max-images 10 --extensions jpg,png

# Custom prompt for all images
python foundry_image_agent.py analyze-batch ./photos/ --prompt "Identify cultural and historical significance"
```

## 📸 Standard Image Analyzer

The **`image_analyzer.py`** provides direct Azure OpenAI GPT-4 Vision analysis without web research.

### Features

- Direct GPT-4 Vision analysis
- Custom prompts support
- Folder batch processing with parallel execution
- JSON output support
- Token usage tracking
- Automatic image optimization

### Setup for Standard Analyzer

Configure Azure OpenAI in `.env`:
```
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key  # optional if using Azure credentials
AZURE_OPENAI_DEPLOYMENT_NAME=your-gpt4-vision-deployment
```

### Usage Examples

#### Basic Analysis
```bash
python image_analyzer.py analyze path/to/your/image.jpg
```

#### Custom Prompt
```bash
python image_analyzer.py analyze image.jpg --prompt "Describe the architectural style and historical period"
```

#### Folder Analysis
```bash
# Analyze all images in folder
python image_analyzer.py analyze-folder ./images/

# Parallel processing with custom settings
python image_analyzer.py analyze-folder ./images/ --parallel 3 --extensions jpg,png --verbose
```

## 🔧 Prerequisites

### AI Foundry Setup (for foundry_image_agent.py)

1. **Azure AI Foundry Project**: Create a project in [Azure AI Foundry](https://ai.azure.com/)
2. **Model Deployment**: Deploy a GPT-4o or GPT-4 Vision model
3. **Bing Grounding Connection**: 
   - Navigate to **Management center** → **Connected resources**
   - Add a **Grounding with Bing Search** connection
   - Note the connection ID (format: `/subscriptions/.../connections/your-connection`)

### Azure OpenAI Setup (for image_analyzer.py)

1. **Azure OpenAI Resource**: Create an Azure OpenAI resource
2. **Model Deployment**: Deploy a GPT-4 Vision model
3. **Endpoint and Key**: Get your endpoint URL and API key

## 📊 Output Examples

### AI Foundry Agent Output

The AI Foundry agent generates comprehensive markdown reports like:

```markdown
# Image Analysis Report

**Analyzed:** 2025-01-31 10:30:15  
**Image:** landmark.jpg  
**Model:** gpt-4o  

## Visual Analysis

### Identified Elements
- **Location**: Eiffel Tower, Paris, France
- **Architecture**: Iron lattice tower, 19th century
- **Context**: Tourist photograph, daytime

### Tags
- landmark, architecture, Paris, France, tourism, iron structure

## Research Findings

### Eiffel Tower Historical Context
[Detailed research with external links...]

### Architectural Significance
[Additional context with web sources...]

---
*Report generated by AI Foundry Image Analysis Agent*
```

### Standard Analyzer Output

```
============================================================
IMAGE ANALYSIS RESULTS
============================================================
Image: landmark.jpg
Model: gpt-4-vision-preview
------------------------------------------------------------
The image shows the iconic Eiffel Tower in Paris, France...
[Analysis content]
------------------------------------------------------------
Token usage - Prompt: 1250, Completion: 445, Total: 1695
```

## 🚀 Getting Started

1. **Quick Start with AI Foundry Agent:**
   ```bash
   # Setup
   pip install -r requirements.txt
   cp .env.template .env
   # Edit .env with your AI Foundry settings
   
   # Test
   python foundry_image_agent.py setup
   
   # Analyze
   python foundry_image_agent.py analyze your-image.jpg
   ```

2. **Quick Start with Standard Analyzer:**
   ```bash
   # Setup  
   pip install -r requirements.txt
   # Edit .env with your Azure OpenAI settings
   
   # Test
   python image_analyzer.py setup
   
   # Analyze
   python image_analyzer.py analyze your-image.jpg
   ```

## 🔍 Advanced Features

### Custom Prompts
Both tools support custom prompts to focus on specific aspects:
- Historical analysis
- Architectural details  
- Cultural significance
- Technical specifications
- Artistic elements

### Batch Processing
- Process entire folders of images
- Generate individual reports or combined analysis
- Support for various image formats
- Progress tracking and error handling

### Output Formats
- **AI Foundry Agent**: Markdown reports with research and external links
- **Standard Analyzer**: JSON output with detailed metadata or console display

## 📋 Requirements

- Python 3.8+
- Azure AI Foundry project (for enhanced agent)
- Azure OpenAI resource (for standard analyzer)
- Internet connection (for Bing research features)

## 🛠️ Troubleshooting

### Common Issues

1. **Missing Dependencies**: Run `pip install -r requirements.txt`
2. **Authentication**: Ensure Azure credentials are configured
3. **Connection ID**: Verify Bing connection ID format for AI Foundry
4. **Model Deployment**: Confirm your model deployment name is correct

### Getting Help

```bash
# Check setup
python foundry_image_agent.py setup
python image_analyzer.py setup

# View help
python foundry_image_agent.py --help
python image_analyzer.py --help
```
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
