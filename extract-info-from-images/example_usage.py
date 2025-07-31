#!/usr/bin/env python3
"""
Example usage script for the AI Foundry Image Agent
This script demonstrates how to use the foundry_image_agent.py programmatically
"""

import os
import sys
from pathlib import Path

# Add the current directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent))

from foundry_image_agent import FoundryImageAgent

def example_single_image_analysis():
    """Example of analyzing a single image"""
    print("=== Single Image Analysis Example ===")
    
    # Check if we have sample images
    inputs_dir = Path("inputs")
    if not inputs_dir.exists():
        print("No inputs directory found. Please add some images to ./inputs/ folder")
        return
    
    # Find first image
    image_files = list(inputs_dir.glob("*.jpg")) + list(inputs_dir.glob("*.jpeg")) + list(inputs_dir.glob("*.png"))
    if not image_files:
        print("No image files found in ./inputs/ directory")
        return
    
    sample_image = image_files[0]
    print(f"Analyzing: {sample_image}")
    
    try:
        # Initialize agent
        agent = FoundryImageAgent()
        
        # Create agent and thread
        agent.create_agent()
        agent.create_thread()
        
        # Analyze image
        result = agent.analyze_image_with_research(
            str(sample_image),
            custom_prompt=(
                "Please analyze this image and identify:\n"
                "1. Any text or signage visible\n"
                "2. The location or setting\n"
                "3. Cultural or historical context\n"
                "4. Any notable objects or people\n"
                "Then research additional information about identified elements."
            )
        )
        
        if result["success"]:
            print("\n" + "="*60)
            print("ANALYSIS RESULT")
            print("="*60)
            print(result["analysis"])
            print("="*60)
            
            # Save result
            output_file = f"example_analysis_{sample_image.stem}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# Analysis of {sample_image.name}\n\n")
                f.write(result["analysis"])
            
            print(f"\nResult saved to: {output_file}")
        else:
            print(f"Analysis failed: {result['error']}")
        
        # Cleanup
        agent.cleanup()
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have:")
        print("1. Configured your .env file with AI Foundry settings")
        print("2. Installed dependencies: pip install -r requirements.txt")
        print("3. Set up Bing grounding connection in AI Foundry")

def check_configuration():
    """Check if the environment is properly configured"""
    print("=== Configuration Check ===")
    
    required_vars = [
        "AZURE_AI_PROJECT_ENDPOINT",
        "BING_CONNECTION_ID"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✓ {var}: {value[:50]}...")
        else:
            print(f"✗ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\nMissing configuration: {', '.join(missing_vars)}")
        print("Please update your .env file with the required values.")
        return False
    
    print("\n✓ Configuration looks good!")
    return True

if __name__ == "__main__":
    print("AI Foundry Image Agent Example")
    print("=" * 40)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check configuration first
    if check_configuration():
        example_single_image_analysis()
    else:
        print("\nPlease fix the configuration and try again.")
        print("See README.md for setup instructions.")
