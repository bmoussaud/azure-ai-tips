#!/usr/bin/env python3
"""
AI Foundry Agent for extracting information from images and enhancing with Bing Search.
This agent analyzes images to extract names, locations, and tags, then uses Bing grounding
to fetch additional information and generate markdown reports with external links.
"""

import os
import sys
import base64
import click
import json
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime
import io

from PIL import Image
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import Connection
from azure.ai.agents.models import BingCustomSearchTool, MessageRole
from azure.ai.agents.models import RunStatus, SubmitToolOutputsAction
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
# Load environment variables
load_dotenv()

# Configure logger for this module
logger = logging.getLogger("image_agent")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s")
handler.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(handler)

class FoundryImageAgent:
    """AI Foundry Agent for image analysis with Bing grounding"""
    
    def __init__(self):
        """Initialize the AI Foundry client and agent"""
        self.project_endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
        self.api_key = os.getenv("AZURE_AI_PROJECT_API_KEY")
        self.bing_connection_id = os.getenv("BING_CONNECTION_ID")
        self.model_deployment_name = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-4o")
        
        if not self.project_endpoint:
            raise ValueError(
                "AZURE_AI_PROJECT_ENDPOINT environment variable is required. "
                "Please set it in your .env file with your AI Foundry project endpoint."
            )
        
        if not self.bing_connection_id:
            raise ValueError(
                "BING_CONNECTION_ID environment variable is required. "
                "Please set it in your .env file with your Bing grounding connection ID."
            )
        
        # Initialize client with Azure credential or API key
        credential = DefaultAzureCredential()
        
        logger.info(f"Connecting to AI Foundry project at {self.project_endpoint} with model {self.model_deployment_name}")
        self.project_client = AIProjectClient(
            endpoint=self.project_endpoint,
            credential=credential
        )
        self.agents_client = self.project_client.agents

        self.agent = None
        self.thread = None
    
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64 string"""
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Validate and optimize image
            try:
                with Image.open(image_path) as img:
                    # Resize if image is too large
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
    
    def create_agent(self):
        """Create an AI agent with Bing grounding capabilities"""
        try:
            # Create Bing grounding tool
            bing_tool = BingCustomSearchTool(connection_id=self._find_connection("GroundingWithCustomSearch").id, instance_name="defaultConfiguration")

            
            tools = [*bing_tool.definitions]
            # Create agent
            agent = self.project_client.agents.create_agent(
                model=self.model_deployment_name,
                name="Image Information Extractor",
                description=(
                    "An AI agent specialized in analyzing images to extract names, locations, "
                    "and tags, then researching additional information using Bing search to "
                    "create comprehensive markdown reports."
                ),
                instructions=(
                    "You are an expert image analyst and researcher. Your task is to:\n"
                    "1. Analyze images to identify:\n"
                    "   - Names of people, places, objects, brands\n"
                    "   - Geographic locations and landmarks\n"
                    "   - Relevant tags and categories\n"
                    "   - Historical or cultural context\n"
                    "2. Use Bing search to find additional information about identified elements\n"
                    "3. Generate comprehensive markdown reports with:\n"
                    "   - Structured analysis of the image\n"
                    "   - Enhanced information from web research\n"
                    "   - Relevant external links and sources\n"
                    "   - Proper citations and references\n"
                    "\n"
                    "Always provide factual, well-researched information and cite your sources."
                ),
                tools=tools
            )
            
            self.agent = agent
            click.echo(f"Created agent with ID: {agent.id}")
            return agent
            
        except Exception as e:
            raise Exception(f"Error creating agent: {e}")
    
    def _find_connection(self, connection_type: str, connection_name: Optional[str] = None) -> Connection:
        """Find a connection by type and (optionally) name. If name is None, return the first connection of the given type."""
        logger.info(f"Searching for connection type '{connection_type}'" + (
            f" with name '{connection_name}'" if connection_name else " (any name)"))
        connections = self.project_client.connections.list(
            connection_type=connection_type)
        if connection_name:
            target = next(filter(lambda c: c.name ==
                          connection_name, connections), None)
        else:
            target = next(iter(connections), None)
        if target:
            logger.info(f"target: {target}")
            logger.info(
                f"Found connection: {target.type} {target.name} (ID: {target.id})")
            return target
        logger.error(f"No connection found for type '{connection_type}'" + (
            f" and name '{connection_name}'" if connection_name else ""))
        raise RuntimeError(f"Connection of type '{connection_type}'" + (
            f" and name '{connection_name}'" if connection_name else "") + " is required but not found")
    
    def create_thread(self):
        """Create a conversation thread"""
        try:
            
            thread = self.agents_client.threads.create()
            self.thread = thread
            click.echo(f"Created thread with ID: {thread.id}")
            return thread
        except Exception as e:
            raise Exception(f"Error creating thread: {e}")
    
    def analyze_image_with_research(self, image_path: str, custom_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Analyze image and research additional information"""
        try:
            logger.info(f"Encoding image: {image_path}")
            base64_image = self.encode_image(image_path)
            
            # Create prompt
            if custom_prompt:
                prompt = custom_prompt
            else:
                prompt = (
                    "Please analyze this content in detail and extract the following information:\n\n"
                    "1. **Names**: Identify any people, places, objects, brands, or text visible\n"
                    "2. **Locations**: Determine geographic locations, landmarks, or settings\n"
                    "3. **Tags**: Generate relevant tags for categorization\n"
                    "4. **Context**: Provide historical, cultural, or situational context\n\n"
                    "After your initial analysis, please research each identified element using Bing search "
                    "to provide additional context, background information, and interesting facts.\n\n"
                    "Format your response as a comprehensive markdown report with:\n"
                    "- Clear headings and sections\n"
                    "- Bullet points for easy reading\n"
                    "- External links to relevant websites\n"
                    "- Proper citations for your sources\n\n"
                    " Output in French language"
                    "Here is the locations to analyze:" + custom_prompt
                )
            
            # Add image to the message
            message_content = [
                {
                    "type": "text",
                    "text": "Content:. Location: Shibuya Parco Tags: Centre commercial, Shopping, Centres commerciaux"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]

            
            self.agents_client.messages.create(
                    thread_id=self.thread.id,
                    role="user",
                    content="Give information about each location:"+ prompt
            )
            
            
            self.agents_client.messages.create(
                thread_id=self.thread.id,
                role="user",
                content=message_content
            )
            
            # Create and run the analysis
            logger.info(f"Starting analysis for image: {image_path}")   
            run = self.agents_client.runs.create_and_process(
                thread_id=self.thread.id,
                agent_id=self.agent.id
            )
            
            # Wait for completion
            while run.status in [RunStatus.QUEUED, RunStatus.IN_PROGRESS, RunStatus.REQUIRES_ACTION]:
                run = self.project_client.agents.get_run(thread_id=self.thread.id, run_id=run.id)
                
                if run.status == RunStatus.REQUIRES_ACTION:
                    # Handle tool calls if needed
                    required_action = run.required_action
                    if isinstance(required_action, SubmitToolOutputsAction):
                        tool_outputs = []
                        for tool_call in required_action.submit_tool_outputs.tool_calls:
                            # Tool outputs are handled automatically by the agent
                            pass
                
                # Small delay to avoid overwhelming the API
                import time
                time.sleep(1)
            
            if run.status == RunStatus.COMPLETED:
                # Get messages from the thread
                messages = self.agents_client.messages.list(
                    thread_id=self.thread.id)
                #for msg in messages:
                #    logger.info(f"===  message: {json.dumps(msg.as_dict(), indent=2)}")

                # Find the assistant's response
                assistant_messages = [msg for msg in messages if msg.role == "assistant"]
                if assistant_messages:
                    latest_message = assistant_messages[0]
                    response_content = ""
                    urls = []
                    
                    for content_item in latest_message.content:
                        if hasattr(content_item, 'text'):
                            response_content += content_item.text.value
                            urls.append([annotation.url_citation for annotation in content_item.text.annotations] )
                    
                
                    # Get run steps for citation information
                    #logger.info("Messages in thread:")
                   

                    """ run_steps = self.project_client.agents.list_run_steps(
                        thread_id=self.thread.id, 
                        run_id=run.id
                    ) """
                    
                     
                    #logger.info(f"Annotation: {urls}")
                    return {
                        "success": True,
                        "analysis": response_content,
                        "image_path": image_path,
                        "run_id": run.id,
                        "thread_id": self.thread.id,
                        "urls": urls,
                        #"run_steps": [step.dict() for step in run_steps.data] if run_steps.data else [],
                        "model": self.model_deployment_name
                    }
                else:
                    return {
                        "success": False,
                        "error": "No response from assistant",
                        "image_path": image_path
                    }
            else:
                return {
                    "success": False,
                    "error": f"Run failed with status: {json.dumps(run.as_dict(), indent=2)}",
                    #"run_info": json.dumps(run.dict(), indent=2),
                    "image_path": image_path
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "image_path": image_path
            }
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.agent:
                self.project_client.agents.delete_agent(self.agent.id)
                click.echo("Deleted agent")
        except Exception as e:
            click.echo(f"Error during cleanup: {e}")


@click.group()
def cli():
    """
    AI Foundry Image Analysis Agent
    
    An intelligent agent that analyzes images to extract names, locations, and tags,
    then researches additional information using Bing search to create comprehensive
    markdown reports with external links.
    
    Commands:
    - analyze: Analyze a single image with research
    - analyze-batch: Analyze multiple images in a folder
    - setup: Check configuration
    
    Setup:
    1. Set environment variables in .env file:
       - AZURE_AI_PROJECT_ENDPOINT=https://your-project.cognitiveservices.azure.com/
       - BING_CONNECTION_ID=/subscriptions/.../connections/your-bing-connection
       - MODEL_DEPLOYMENT_NAME=gpt-4o (optional)
       - AZURE_AI_PROJECT_API_KEY=your-key (optional if using Azure credentials)
    
    2. Install dependencies: pip install -r requirements.txt
    
    3. Run: python foundry_image_agent.py analyze path/to/image.jpg
    """
    pass

@cli.command()
def setup():
    """Check setup and configuration"""
    click.echo("Checking AI Foundry setup...")
    
    required_vars = [
        "AZURE_AI_PROJECT_ENDPOINT",
        "BING_CONNECTION_ID"
    ]
    
    optional_vars = [
        "AZURE_AI_PROJECT_API_KEY",
        "MODEL_DEPLOYMENT_NAME"
    ]
    
    click.echo("\nRequired environment variables:")
    for var in required_vars:
        value = os.getenv(var)
        status = "✓" if value else "✗"
        display_value = value[:50] + "..." if value and len(value) > 50 else (value if value else "Not set")
        click.echo(f"  {status} {var}: {display_value}")
    
    click.echo("\nOptional environment variables:")
    for var in optional_vars:
        value = os.getenv(var)
        status = "✓" if value else "-"
        display_value = value if value else "Using default/credential"
        click.echo(f"  {status} {var}: {display_value}")
    
    # Test connection if endpoint is available
    endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    bing_connection = os.getenv("BING_CONNECTION_ID")
    
    if endpoint and bing_connection:
        try:
            agent = FoundryImageAgent()
            click.echo(f"\n✓ Successfully initialized AI Foundry client")
        except Exception as e:
            click.echo(f"\n✗ Failed to initialize client: {e}")

@cli.command()
@click.argument('image_path', type=click.Path(exists=True))
@click.option('--prompt', '-p', help='Custom prompt for image analysis')
@click.option('--output', '-o', type=click.Path(), help='Output file for markdown report')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--keep-agent', '-k', is_flag=True, help='Keep agent after analysis (for multiple runs)')
def analyze(image_path: str, prompt: Optional[str], output: Optional[str], verbose: bool, keep_agent: bool):
    """
    Analyze an image and research additional information using AI Foundry Agent with Bing grounding.
    
    IMAGE_PATH: Path to the image file to analyze
    """
    agent_client = None
    try:
        if verbose:
            click.echo(f"Initializing AI Foundry Agent...")
        
        # Initialize agent
        agent_client = FoundryImageAgent()
        
        # Create agent and thread
        agent_client.create_agent()
        agent_client.create_thread()
        
        if verbose:
            click.echo(f"Analyzing image: {image_path}")
            if prompt:
                click.echo(f"Using custom prompt: {prompt}")
        
        # Analyze image with research
        click.echo("Analyzing image and researching information...")
        result = agent_client.analyze_image_with_research(image_path, prompt)
        
        if result["success"]:
            click.echo("\n" + "="*80)
            click.echo("IMAGE ANALYSIS & RESEARCH REPORT")
            click.echo("="*80)
            click.echo(f"Image: {result['image_path']}")
            click.echo(f"Model: {result['model']}")
            click.echo(f"Analysis ID: {result['run_id']}")
            click.echo("-"*80)
            click.echo(result["analysis"])
            click.echo("-"*80)
            
            # Save to output file
            if output:
                output_path = Path(output)
            else:
                # Generate default filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_name = Path(image_path).stem
                output_path = Path(f"image_analysis_{image_name}_{timestamp}.md")
            
            # Create comprehensive markdown report
            markdown_content = f"""# Image Analysis Report

**Analyzed:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Image:** {os.path.basename(image_path)}  
**Model:** {result['model']}  
**Analysis ID:** {result['run_id']}

---

{result['analysis']}

---

*Report generated by AI Foundry Image Analysis Agent*
"""
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            click.echo(f"\nMarkdown report saved to: {output_path}")
            
            if verbose and result.get("run_steps"):
                click.echo(f"\nRun steps summary: {len(result['run_steps'])} steps executed")
        
        else:
            click.echo(f"Error analyzing image: {result['error']}", err=True)
            logger.error(f"Analysis failed: {result['error']}", exc_info=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)
    
    finally:
        # Cleanup unless keeping agent
        if agent_client and not keep_agent:
            agent_client.cleanup()

@cli.command()
@click.argument('folder_path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--prompt', '-p', help='Custom prompt for image analysis')
@click.option('--output-dir', '-o', type=click.Path(), help='Output directory for reports (default: ./reports)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--extensions', '-e', default='jpg,jpeg,png,gif,bmp,tiff,webp', 
              help='Comma-separated list of image extensions to process')
@click.option('--max-images', '-m', type=int, help='Maximum number of images to process')
def analyze_batch(folder_path: str, prompt: Optional[str], output_dir: Optional[str], 
                 verbose: bool, extensions: str, max_images: Optional[int]):
    """
    Analyze multiple images in a folder and generate individual research reports.
    
    FOLDER_PATH: Path to the folder containing images to analyze
    """
    import glob
    
    agent_client = None
    try:
        if verbose:
            click.echo(f"Scanning folder: {folder_path}")
        
        # Parse extensions and find images
        ext_list = [ext.strip().lower() for ext in extensions.split(',')]
        image_files = []
        
        for ext in ext_list:
            pattern = os.path.join(folder_path, f"**/*.{ext}")
            image_files.extend(glob.glob(pattern, recursive=True))
            pattern = os.path.join(folder_path, f"**/*.{ext.upper()}")
            image_files.extend(glob.glob(pattern, recursive=True))
        
        image_files = sorted(list(set(image_files)))
        
        if not image_files:
            click.echo(f"No image files found in {folder_path}")
            return
        
        # Limit number of images if specified
        if max_images and len(image_files) > max_images:
            image_files = image_files[:max_images]
            click.echo(f"Limited to first {max_images} images")
        
        # Setup output directory
        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = Path("./reports")
        
        output_path.mkdir(exist_ok=True)
        
        click.echo(f"Found {len(image_files)} images to analyze")
        
        # Initialize agent (reuse for all images)
        agent_client = FoundryImageAgent()
        agent_client.create_agent()
        agent_client.create_thread()
        
        # Process each image
        results = []
        
        with click.progressbar(image_files, label="Analyzing images") as bar:
            for image_file in bar:
                try:
                    if verbose:
                        click.echo(f"\nProcessing: {os.path.relpath(image_file, folder_path)}")
                    
                    result = agent_client.analyze_image_with_research(image_file, prompt)
                    
                    if result["success"]:
                        # Generate report filename
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        image_name = Path(image_file).stem
                        report_filename = f"analysis_{image_name}_{timestamp}.md"
                        report_path = output_path / report_filename
                        
                        # Create markdown report
                        markdown_content = f"""# Image Analysis Report

**Analyzed:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Image:** {os.path.basename(image_file)}  
**Relative Path:** {os.path.relpath(image_file, folder_path)}  
**Model:** {result['model']}  
**Analysis ID:** {result['run_id']}

---

{result['analysis']}

---

*Report generated by AI Foundry Image Analysis Agent*
"""
                        
                        with open(report_path, 'w', encoding='utf-8') as f:
                            f.write(markdown_content)
                        
                        result["report_path"] = str(report_path)
                        results.append(result)
                        
                        if verbose:
                            click.echo(f"Saved report: {report_path}")
                    
                    else:
                        click.echo(f"Failed to analyze {image_file}: {result['error']}")
                        results.append(result)
                
                except Exception as e:
                    click.echo(f"Error processing {image_file}: {e}")
                    results.append({
                        "success": False,
                        "error": str(e),
                        "image_path": image_file
                    })
        
        # Generate summary report
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful
        
        summary_content = f"""# Batch Analysis Summary

**Processed:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Folder:** {folder_path}  
**Total Images:** {len(image_files)}  
**Successful:** {successful}  
**Failed:** {failed}

## Successful Analyses

"""
        
        for result in results:
            if result["success"]:
                summary_content += f"- [{os.path.basename(result['image_path'])}]({os.path.basename(result['report_path'])})\n"
        
        if failed > 0:
            summary_content += "\n## Failed Analyses\n\n"
            for result in results:
                if not result["success"]:
                    summary_content += f"- {os.path.basename(result['image_path'])}: {result['error']}\n"
        
        summary_content += "\n---\n\n*Summary generated by AI Foundry Image Analysis Agent*\n"
        
        summary_path = output_path / "batch_summary.md"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        click.echo(f"\nBatch analysis complete!")
        click.echo(f"Reports saved to: {output_path}")
        click.echo(f"Summary: {summary_path}")
        click.echo(f"Successfully analyzed: {successful}/{len(image_files)} images")
        
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)
    
    finally:
        if agent_client:
            agent_client.cleanup()


if __name__ == '__main__':
    cli()
