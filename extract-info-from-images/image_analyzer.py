#!/usr/bin/env python3
"""
CLI tool for extracting information from images using Azure OpenAI GPT-4 Vision
"""

import os
import sys
import base64
import click
from pathlib import Path
from typing import Optional
import json
from PIL import Image
import io

try:
    from openai import AzureOpenAI
    from azure.identity import DefaultAzureCredential
    from dotenv import load_dotenv
except ImportError as e:
    click.echo(f"Error: Missing required dependency: {e}")
    click.echo("Please install dependencies with: pip install -r requirements.txt")
    sys.exit(1)

# Load environment variables
load_dotenv()

class ImageAnalyzer:
    """Azure OpenAI GPT-4 Vision image analyzer"""
    
    def __init__(self):
        """Initialize the Azure OpenAI client"""
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "extimage-gpt-4.1-mini")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
        
        if not self.endpoint:
            raise ValueError(
                "AZURE_OPENAI_ENDPOINT environment variable is required. "
                "Please set it or create a .env file with your Azure OpenAI endpoint."
            )
        
        # Initialize client with Azure credential or API key
        if self.api_key:
            self.client = AzureOpenAI(
                api_key=self.api_key,
                api_version=self.api_version,
                azure_endpoint=self.endpoint
            )
        else:
            # Use Azure Default Credential (recommended for production)
            credential = DefaultAzureCredential()
            self.client = AzureOpenAI(
                azure_ad_token_provider=lambda: credential.get_token("https://cognitiveservices.azure.com/.default").token,
                api_version=self.api_version,
                azure_endpoint=self.endpoint
            )
    
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64 string"""
        try:
            # Validate image file
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Check if it's a valid image
            try:
                with Image.open(image_path) as img:
                    # Resize if image is too large (OpenAI has size limits)
                    max_size = (2048, 2048)
                    if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                        img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    
                    # Convert to RGB if necessary
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    
                    # Save to bytes
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='JPEG', quality=85)
                    img_byte_arr = img_byte_arr.getvalue()
                    
                    return base64.b64encode(img_byte_arr).decode('utf-8')
            
            except Exception as e:
                raise ValueError(f"Invalid image file: {e}")
                
        except Exception as e:
            raise Exception(f"Error processing image: {e}")
    
    def analyze_image(self, image_path: str, prompt: Optional[str] = None, max_tokens: int = 2000) -> dict:
        """Analyze image using GPT-4 Vision"""
        try:
            # Encode image
            base64_image = self.encode_image(image_path)
            
            # Default prompt if none provided
            if not prompt:
                prompt = (
                    "Analyze this image in detail. Describe what you see, including:"
                    "- Main objects, people, or subjects"
                    "- Text content (if any)"
                    "- Colors, setting, and atmosphere"
                    "- Any notable details or interesting features"
                    "- Context or purpose of the image"
                    "Provide a comprehensive but organized description."
                )
            
            # Prepare the message
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
            
            # Call Azure OpenAI
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.3
            )
            
            return {
                "success": True,
                "analysis": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "model": self.deployment_name,
                "image_path": image_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "image_path": image_path
            }


@click.command()
@click.argument('image_path', type=click.Path(exists=True))
@click.option('--prompt', '-p', help='Custom prompt for image analysis')
@click.option('--max-tokens', '-t', default=2000, help='Maximum tokens for response')
@click.option('--output', '-o', type=click.Path(), help='Output file for results (JSON)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def analyze(image_path: str, prompt: Optional[str], max_tokens: int, output: Optional[str], verbose: bool):
    """
    Extract information from an image using Azure OpenAI GPT-4 Vision.
    
    IMAGE_PATH: Path to the image file to analyze
    """
    try:
        if verbose:
            click.echo(f"Initializing Azure OpenAI client...")
        
        # Initialize analyzer
        analyzer = ImageAnalyzer()
        
        if verbose:
            click.echo(f"Analyzing image: {image_path}")
            if prompt:
                click.echo(f"Using custom prompt: {prompt}")
        
        # Analyze image
        result = analyzer.analyze_image(image_path, prompt, max_tokens)
        
        if result["success"]:
            click.echo("\n" + "="*60)
            click.echo("IMAGE ANALYSIS RESULTS")
            click.echo("="*60)
            click.echo(f"Image: {result['image_path']}")
            click.echo(f"Model: {result['model']}")
            click.echo("-"*60)
            click.echo(result["analysis"])
            click.echo("-"*60)
            
            if verbose:
                usage = result["usage"]
                click.echo(f"Token usage - Prompt: {usage['prompt_tokens']}, "
                          f"Completion: {usage['completion_tokens']}, "
                          f"Total: {usage['total_tokens']}")
            
            # Save to output file if specified
            if output:
                with open(output, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                click.echo(f"\nResults saved to: {output}")
        
        else:
            click.echo(f"Error analyzing image: {result['error']}", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@click.group()
def cli():
    """
    Azure OpenAI GPT-4 Vision Image Analysis CLI
    
    Extract detailed information from images using Azure OpenAI's GPT-4 Vision model.
    
    Commands:
    - analyze: Analyze a single image
    - analyze-folder: Analyze all images in a folder
    - setup: Check configuration
    
    Setup:
    1. Set environment variables in .env file:
       - AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
       - AZURE_OPENAI_API_KEY=your-api-key (optional if using Azure credentials)
       - AZURE_OPENAI_DEPLOYMENT_NAME=your-gpt4-vision-deployment
    
    2. Install dependencies: pip install -r requirements.txt
    
    3. Run: python image_analyzer.py analyze path/to/image.jpg
           python image_analyzer.py analyze-folder path/to/images/
    """
    pass

@cli.command()
def setup():
    """Check setup and configuration"""
    click.echo("Checking Azure OpenAI setup...")
    
    required_vars = [
        "AZURE_OPENAI_ENDPOINT",
    ]
    
    optional_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_DEPLOYMENT_NAME", 
        "AZURE_OPENAI_API_VERSION"
    ]
    
    click.echo("\nRequired environment variables:")
    for var in required_vars:
        value = os.getenv(var)
        status = "✓" if value else "✗"
        click.echo(f"  {status} {var}: {'Set' if value else 'Not set'}")
    
    click.echo("\nOptional environment variables:")
    for var in optional_vars:
        value = os.getenv(var)
        status = "✓" if value else "-"
        display_value = value if value else "Using default/credential"
        click.echo(f"  {status} {var}: {display_value}")
    
    # Test connection if endpoint is available
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    if endpoint:
        try:
            analyzer = ImageAnalyzer()
            click.echo(f"\n✓ Successfully initialized Azure OpenAI client")
        except Exception as e:
            click.echo(f"\n✗ Failed to initialize client: {e}")

@cli.command()
@click.argument('folder_path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--prompt', '-p', help='Custom prompt for image analysis')
@click.option('--max-tokens', '-t', default=2000, help='Maximum tokens for response per image')
@click.option('--output', '-o', type=click.Path(), help='Output file for results (JSON)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--extensions', '-e', default='jpg,jpeg,png,gif,bmp,tiff,webp', 
              help='Comma-separated list of image extensions to process (default: jpg,jpeg,png,gif,bmp,tiff,webp)')
@click.option('--parallel', '-j', default=1, type=int, help='Number of parallel processing threads (default: 1)')
def analyze_folder(folder_path: str, prompt: Optional[str], max_tokens: int, output: Optional[str], 
                  verbose: bool, extensions: str, parallel: int):
    """
    Analyze all images in a folder using Azure OpenAI GPT-4 Vision.
    
    FOLDER_PATH: Path to the folder containing images to analyze
    """
    import glob
    import threading
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from datetime import datetime
    
    try:
        if verbose:
            click.echo(f"Scanning folder: {folder_path}")
        
        # Parse extensions
        ext_list = [ext.strip().lower() for ext in extensions.split(',')]
        
        # Find all image files
        image_files = []
        for ext in ext_list:
            pattern = os.path.join(folder_path, f"**/*.{ext}")
            image_files.extend(glob.glob(pattern, recursive=True))
            # Also check uppercase extensions
            pattern = os.path.join(folder_path, f"**/*.{ext.upper()}")
            image_files.extend(glob.glob(pattern, recursive=True))
        
        # Remove duplicates and sort
        image_files = sorted(list(set(image_files)))
        
        if not image_files:
            click.echo(f"No image files found in {folder_path} with extensions: {extensions}")
            return
        
        if verbose:
            click.echo(f"Found {len(image_files)} image files")
            for img in image_files:
                click.echo(f"  - {os.path.relpath(img, folder_path)}")
        
        # Initialize analyzer
        analyzer = ImageAnalyzer()
        
        # Results storage
        results = {
            "folder_path": folder_path,
            "analyzed_at": datetime.now().isoformat(),
            "total_images": len(image_files),
            "successful_analyses": 0,
            "failed_analyses": 0,
            "prompt_used": prompt or "Default analysis prompt",
            "images": []
        }
        
        def analyze_single_image(img_path):
            """Analyze a single image and return result"""
            try:
                if verbose:
                    click.echo(f"Processing: {os.path.relpath(img_path, folder_path)}")
                
                result = analyzer.analyze_image(img_path, prompt, max_tokens)
                result["relative_path"] = os.path.relpath(img_path, folder_path)
                return result
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "image_path": img_path,
                    "relative_path": os.path.relpath(img_path, folder_path)
                }
        
        # Process images
        if parallel > 1:
            # Parallel processing
            if verbose:
                click.echo(f"Processing images with {parallel} threads...")
            
            with ThreadPoolExecutor(max_workers=parallel) as executor:
                # Submit all jobs
                future_to_image = {executor.submit(analyze_single_image, img): img for img in image_files}
                
                # Collect results as they complete
                with click.progressbar(as_completed(future_to_image), length=len(image_files),
                                     label="Analyzing images") as bar:
                    for future in bar:
                        result = future.result()
                        results["images"].append(result)
                        if result["success"]:
                            results["successful_analyses"] += 1
                        else:
                            results["failed_analyses"] += 1
        else:
            # Sequential processing
            with click.progressbar(image_files, label="Analyzing images") as bar:
                for img_path in bar:
                    result = analyze_single_image(img_path)
                    results["images"].append(result)
                    if result["success"]:
                        results["successful_analyses"] += 1
                    else:
                        results["failed_analyses"] += 1
        
        # Sort results by relative path for consistent output
        results["images"].sort(key=lambda x: x.get("relative_path", ""))
        
        # Calculate summary statistics
        total_tokens = sum(r.get("usage", {}).get("total_tokens", 0) for r in results["images"] if r["success"])
        results["total_tokens_used"] = total_tokens
        
        # Display summary
        click.echo("\n" + "="*60)
        click.echo("FOLDER ANALYSIS SUMMARY")
        click.echo("="*60)
        click.echo(f"Folder: {folder_path}")
        click.echo(f"Total images found: {results['total_images']}")
        click.echo(f"Successfully analyzed: {results['successful_analyses']}")
        click.echo(f"Failed analyses: {results['failed_analyses']}")
        click.echo(f"Total tokens used: {total_tokens}")
        click.echo("="*60)
        
        # Display individual results if verbose or small number of images
        if verbose or len(image_files) <= 5:
            for result in results["images"]:
                #
                # click.echo(f"\n--- {result['relative_path']} ---")
                click.echo(f"\n--------------")
                if result["success"]:
                    click.echo(result["analysis"])
                    #if verbose:
                    #    usage = result.get("usage", {})
                    #    click.echo(f"[Tokens: {usage.get('total_tokens', 'N/A')}]")
                else:
                    click.echo(f"ERROR: {result['error']}")
        elif results["successful_analyses"] > 0:
            click.echo(f"\nUse --verbose flag to see individual analysis results, or check the output file.")
        
        # Show failed images if any
        if results["failed_analyses"] > 0:
            click.echo(f"\nFailed to analyze {results['failed_analyses']} images:")
            for result in results["images"]:
                if not result["success"]:
                    click.echo(f"  ✗ {result['relative_path']}: {result['error']}")
        
        # Save to output file
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            click.echo(f"\nDetailed results saved to: {output}")
        else:
            # Default output file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_output = f"image_analysis_{timestamp}.json"
            with open(default_output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            click.echo(f"\nDetailed results saved to: {default_output}")

        # dump all the analysis to the output file
        #if verbose:
        #    click.echo("\nFull analysis results:")
        #    click.echo(json.dumps(results, indent=2, ensure_ascii=False))
            
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)

cli.add_command(analyze)
cli.add_command(analyze_folder)

if __name__ == '__main__':
    cli()
