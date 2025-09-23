#!/usr/bin/env python3

"""
Test script to verify PDF metadata functionality
This script tests that the creator field is properly set in generated PDFs
"""

import os
import sys
from datetime import datetime

try:
    import requests
    from pypdf import PdfReader
except ImportError as e:
    print(f"Required dependency missing: {e}")
    print("Install with: pip install requests pypdf")
    sys.exit(1)

# Configuration
PORT = os.getenv("PORT", "8822")
BASE_URL = f"http://localhost:{PORT}"
API_KEY = os.getenv("API_KEY", "your-secret-api-key-here")

# Headers for authentication
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}


def test_server_health():
    """Test if the server is running and healthy."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✓ Server is healthy: {health_data.get('status')}")
            return True
        else:
            print(f"✗ Health check failed with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to server at {BASE_URL}")
        print("Make sure the server is running with: python main.py")
        return False
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False


def extract_pdf_metadata(pdf_bytes):
    """Extract metadata from PDF bytes."""
    try:
        import io

        pdf_stream = io.BytesIO(pdf_bytes)
        reader = PdfReader(pdf_stream)
        metadata = reader.metadata
        return metadata
    except Exception as e:
        print(f"Error reading PDF metadata: {e}")
        return None


def test_html_without_creator():
    """Test HTML to PDF conversion without creator field."""
    print("\n🧪 Testing HTML conversion without creator field...")

    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Without Creator</title>
    </head>
    <body>
        <h1>Test PDF Without Creator</h1>
        <p>This PDF should not have a custom creator field.</p>
    </body>
    </html>
    """

    payload = {"html": html_content, "options": {"format": "A4"}}

    try:
        response = requests.post(f"{BASE_URL}/convert", headers=HEADERS, json=payload)

        if response.status_code == 200:
            metadata = extract_pdf_metadata(response.content)
            if metadata:
                creator = metadata.get("/Creator", "Not set")
                print("✓ PDF generated successfully")
                print(f"  Creator field: {creator}")
                return True
            else:
                print("✗ Could not read PDF metadata")
                return False
        else:
            print(f"✗ Conversion failed with status {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def test_html_with_creator():
    """Test HTML to PDF conversion with custom creator field."""
    print("\n🧪 Testing HTML conversion with custom creator field...")

    custom_creator = "Test PDF Generator v1.0"

    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test With Creator</title>
    </head>
    <body>
        <h1>Test PDF With Creator</h1>
        <p>This PDF should have a custom creator field set.</p>
    </body>
    </html>
    """

    payload = {"html": html_content, "options": {"format": "A4"}, "creator": custom_creator}

    try:
        response = requests.post(f"{BASE_URL}/convert", headers=HEADERS, json=payload)

        if response.status_code == 200:
            metadata = extract_pdf_metadata(response.content)
            if metadata:
                creator = metadata.get("/Creator", "Not set")
                print("✓ PDF generated successfully")
                print(f"  Expected creator: {custom_creator}")
                print(f"  Actual creator: {creator}")

                if creator == custom_creator:
                    print("✓ Creator field matches expected value!")
                    return True
                else:
                    print("✗ Creator field does not match expected value")
                    return False
            else:
                print("✗ Could not read PDF metadata")
                return False
        else:
            print(f"✗ Conversion failed with status {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def test_url_with_creator():
    """Test URL to PDF conversion with custom creator field."""
    print("\n🧪 Testing URL conversion with custom creator field...")

    custom_creator = "URL PDF Generator v2.0"
    test_url = "https://httpbin.org/html"

    payload = {"url": test_url, "options": {"format": "A4"}, "creator": custom_creator}

    try:
        response = requests.post(f"{BASE_URL}/convert-url", headers=HEADERS, params=payload)

        if response.status_code == 200:
            metadata = extract_pdf_metadata(response.content)
            if metadata:
                creator = metadata.get("/Creator", "Not set")
                print("✓ URL PDF generated successfully")
                print(f"  Expected creator: {custom_creator}")
                print(f"  Actual creator: {creator}")

                if creator == custom_creator:
                    print("✓ Creator field matches expected value!")
                    return True
                else:
                    print("✗ Creator field does not match expected value")
                    return False
            else:
                print("✗ Could not read PDF metadata")
                return False
        else:
            print(f"✗ URL conversion failed with status {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def test_empty_creator():
    """Test HTML to PDF conversion with empty creator field."""
    print("\n🧪 Testing HTML conversion with empty creator field...")

    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Empty Creator</title>
    </head>
    <body>
        <h1>Test PDF With Empty Creator</h1>
        <p>This PDF has an empty creator field.</p>
    </body>
    </html>
    """

    payload = {"html": html_content, "options": {"format": "A4"}, "creator": ""}

    try:
        response = requests.post(f"{BASE_URL}/convert", headers=HEADERS, json=payload)

        if response.status_code == 200:
            metadata = extract_pdf_metadata(response.content)
            if metadata:
                creator = metadata.get("/Creator", "Not set")
                print("✓ PDF generated successfully")
                print(f"  Creator field: '{creator}'")
                # Empty creator should not modify the PDF
                return True
            else:
                print("✗ Could not read PDF metadata")
                return False
        else:
            print(f"✗ Conversion failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def save_sample_pdf():
    """Generate and save a sample PDF with metadata for manual inspection."""
    print("\n📁 Generating sample PDF for manual inspection...")

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sample PDF with Metadata</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .metadata-box {{ background: #f0f8ff; padding: 20px; border-radius: 8px; border: 1px solid #007acc; }}
            .highlight {{ background: #ffff99; padding: 2px 4px; }}
        </style>
    </head>
    <body>
        <h1>Sample PDF with Custom Metadata</h1>
        <div class="metadata-box">
            <h2>Metadata Information</h2>
            <p><strong>Creator:</strong> <span class="highlight">PDF Metadata Test Suite v1.0</span></p>
            <p><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p><strong>Purpose:</strong> Demonstrate custom PDF creator metadata</p>
        </div>

        <h2>How to Check Metadata</h2>
        <ol>
            <li>Right-click on this PDF file</li>
            <li>Select "Properties" (or "Document Properties")</li>
            <li>Look for the "Creator" field in the metadata</li>
            <li>It should show: "PDF Metadata Test Suite v1.0"</li>
        </ol>
    </body>
    </html>
    """

    payload = {
        "html": html_content,
        "options": {"format": "A4", "margin": {"top": "2cm", "right": "2cm", "bottom": "2cm", "left": "2cm"}},
        "creator": "PDF Metadata Test Suite v1.0",
    }

    try:
        response = requests.post(f"{BASE_URL}/convert", headers=HEADERS, json=payload)

        if response.status_code == 200:
            filename = f"sample_with_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            with open(filename, "wb") as f:
                f.write(response.content)

            print(f"✓ Sample PDF saved as: {filename}")
            print("  Right-click the file and check Properties to view the creator metadata!")
            return True
        else:
            print(f"✗ Failed to generate sample PDF: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Failed to save sample PDF: {e}")
        return False


def main():
    """Run all metadata tests."""
    print("PDF Creator Metadata Test Suite")
    print("=" * 50)
    print(f"Testing server at: {BASE_URL}")
    print(f"API Key: {'*' * (len(API_KEY) - 4) + API_KEY[-4:] if len(API_KEY) > 4 else '****'}")

    # List of test functions
    tests = [
        ("Server Health Check", test_server_health),
        ("HTML without Creator", test_html_without_creator),
        ("HTML with Creator", test_html_with_creator),
        ("URL with Creator", test_url_with_creator),
        ("Empty Creator Field", test_empty_creator),
        ("Save Sample PDF", save_sample_pdf),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{'=' * 20} {test_name} {'=' * 20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} - PASSED")
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")

    # Summary
    print(f"\n{'=' * 50}")
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! PDF creator metadata is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
