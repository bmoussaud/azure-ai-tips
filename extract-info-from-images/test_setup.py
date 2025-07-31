#!/usr/bin/env python3
"""
Quick test script to validate the AI Foundry setup
Run this before using the full agent to ensure everything is configured correctly
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Test if all required packages can be imported"""
    print("Testing imports...")
    
    try:
        import click
        print("✓ click")
    except ImportError:
        print("✗ click - run: pip install click")
        return False
    
    try:
        from PIL import Image
        print("✓ PIL (Pillow)")
    except ImportError:
        print("✗ PIL - run: pip install pillow")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✓ python-dotenv")
    except ImportError:
        print("✗ python-dotenv - run: pip install python-dotenv")
        return False
    
    try:
        from azure.identity import DefaultAzureCredential
        print("✓ azure-identity")
    except ImportError:
        print("✗ azure-identity - run: pip install azure-identity")
        return False
    
    try:
        from azure.ai.projects import AIProjectClient
        print("✓ azure-ai-projects")
    except ImportError:
        print("✗ azure-ai-projects - run: pip install azure-ai-projects")
        return False
    
    print("All imports successful!\n")
    return True

def test_environment():
    """Test environment configuration"""
    print("Testing environment configuration...")
    
    # Load .env file if it exists
    env_file = Path(".env")
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv()
        print("✓ .env file loaded")
    else:
        print("⚠ No .env file found (using system environment)")
    
    # Check required variables
    required_vars = {
        "AZURE_AI_PROJECT_ENDPOINT": "Your AI Foundry project endpoint",
        "BING_CONNECTION_ID": "Your Bing grounding connection ID"
    }
    
    all_good = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✓ {var}: {value[:50]}...")
        else:
            print(f"✗ {var}: Not set ({description})")
            all_good = False
    
    # Check optional variables
    optional_vars = {
        "MODEL_DEPLOYMENT_NAME": "gpt-4o (default)",
        "AZURE_AI_PROJECT_API_KEY": "Uses Azure credentials if not set"
    }
    
    print("\nOptional variables:")
    for var, default in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✓ {var}: {value}")
        else:
            print(f"- {var}: Not set ({default})")
    
    return all_good

def test_azure_connection():
    """Test Azure connection (basic check)"""
    print("\nTesting Azure connection...")
    
    endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    if not endpoint:
        print("✗ Cannot test connection - no endpoint configured")
        return False
    
    try:
        from azure.identity import DefaultAzureCredential
        from azure.ai.projects import AIProjectClient
        
        # Try to initialize client
        credential = DefaultAzureCredential()
        client = AIProjectClient.from_connection_string(
            conn_str=endpoint,
            credential=credential
        )
        print("✓ AI Foundry client initialized successfully")
        return True
        
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print("  This might be due to authentication or network issues")
        return False

def main():
    """Run all tests"""
    print("AI Foundry Image Agent - Setup Validation")
    print("=" * 50)
    
    # Test 1: Imports
    if not test_imports():
        print("\n❌ Import test failed. Please install missing packages.")
        print("Run: pip install -r requirements.txt")
        return
    
    # Test 2: Environment
    if not test_environment():
        print("\n❌ Environment test failed. Please configure your .env file.")
        print("Copy .env.template to .env and fill in your values.")
        return
    
    # Test 3: Azure connection (optional)
    connection_ok = test_azure_connection()
    
    # Summary
    print("\n" + "=" * 50)
    print("SETUP VALIDATION SUMMARY")
    print("=" * 50)
    print("✓ Package imports: OK")
    print("✓ Environment config: OK")
    print(f"{'✓' if connection_ok else '⚠'} Azure connection: {'OK' if connection_ok else 'Check auth/network'}")
    
    if connection_ok:
        print("\n🎉 Setup looks good! You can now use:")
        print("   python foundry_image_agent.py analyze your-image.jpg")
    else:
        print("\n⚠ Setup mostly ready. Connection issues might be:")
        print("   - Authentication: Run 'az login' or configure service principal")
        print("   - Network: Check firewall/proxy settings")
        print("   - Permissions: Ensure proper Azure RBAC roles")

if __name__ == "__main__":
    main()
