#!/usr/bin/env python3
"""
Test script for the new /upload endpoint.
This script demonstrates how to upload a file and get the expected response format.
"""

import requests
import os
from io import BytesIO

def create_test_image():
    """Create a simple test image file in memory (fake JPEG header)."""
    # Create a minimal JPEG-like file for testing
    # This is just for testing - not a real image
    fake_jpeg = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00' + b'\x00' * 100
    return BytesIO(fake_jpeg)

def test_upload_endpoint(server_url="http://localhost:8080", user_id="test_user_123"):
    """Test the upload endpoint with a sample image."""
    
    print(f"🧪 Testing upload endpoint at {server_url}/upload")
    
    # Create test image
    test_image = create_test_image()
    
    # Prepare the files and data for the request
    files = {
        'file': ('test_receipt.jpg', test_image, 'image/jpeg')
    }
    data = {
        'userId': user_id
    }
    
    try:
        # Make the POST request
        response = requests.post(f"{server_url}/upload", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload successful!")
            print(f"📸 Image URL: {result.get('imageUrl')}")
            print(f"👤 User ID: {result.get('userId')}")
            print(f"📋 Full response: {result}")
            
            # Verify the response format matches expectations
            expected_keys = {'imageUrl', 'userId'}
            actual_keys = set(result.keys())
            
            if expected_keys == actual_keys:
                print("✅ Response format matches expected structure")
            else:
                print(f"⚠️  Response format mismatch. Expected: {expected_keys}, Got: {actual_keys}")
            
            return result
        else:
            print(f"❌ Upload failed with status code: {response.status_code}")
            print(f"Error details: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to server at {server_url}")
        print("Make sure the server is running with: python simple_server.py or python adk_main.py")
        return None
    except Exception as e:
        print(f"❌ Error during upload test: {e}")
        return None

def test_with_actual_file(file_path, server_url="http://localhost:8080", user_id="test_user_123"):
    """Test the upload endpoint with an actual file."""
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return None
    
    print(f"🧪 Testing upload endpoint with file: {file_path}")
    
    try:
        with open(file_path, 'rb') as f:
            files = {
                'file': (os.path.basename(file_path), f, 'image/jpeg')
            }
            data = {
                'userId': user_id
            }
            
            response = requests.post(f"{server_url}/upload", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Upload successful!")
                print(f"📸 Image URL: {result.get('imageUrl')}")
                print(f"👤 User ID: {result.get('userId')}")
                return result
            else:
                print(f"❌ Upload failed with status code: {response.status_code}")
                print(f"Error details: {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ Error during file upload test: {e}")
        return None

def main():
    """Main test function."""
    print("🚀 Starting upload endpoint tests...")
    
    # Test with generated image
    print("\n" + "="*50)
    print("Test 1: Upload with generated test image")
    print("="*50)
    result1 = test_upload_endpoint()
    
    # Test with actual file if available
    print("\n" + "="*50)
    print("Test 2: Upload with actual file (if available)")
    print("="*50)
    
    # Look for any image files in the current directory
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    test_files = []
    
    for file in os.listdir('.'):
        if any(file.lower().endswith(ext) for ext in image_extensions):
            test_files.append(file)
    
    if test_files:
        print(f"Found test image files: {test_files}")
        result2 = test_with_actual_file(test_files[0])
    else:
        print("No image files found in current directory for testing")
        result2 = None
    
    # Test both servers if they're different
    print("\n" + "="*50)
    print("Test 3: Test ADK server endpoint (if different)")
    print("="*50)
    
    # The ADK server might be running on the same port, but let's test anyway
    adk_result = test_upload_endpoint(server_url="http://localhost:8080", user_id="adk_test_user")
    
    print("\n🎯 Test Summary:")
    print(f"Generated image test: {'✅ Passed' if result1 else '❌ Failed'}")
    print(f"Actual file test: {'✅ Passed' if result2 else '❌ Failed or skipped'}")
    print(f"ADK server test: {'✅ Passed' if adk_result else '❌ Failed'}")

if __name__ == "__main__":
    main()
