#!/usr/bin/env python3

"""
Test script for Chromium HTML to PDF Server
Demonstrates API functionality with various test cases
"""

import os
import sys
from datetime import datetime

import requests

# Configuration
PORT = os.getenv("PORT", "8822")
BASE_URL = f"http://localhost:{PORT}"
API_KEY = os.getenv("API_KEY", "your-secret-api-key-here")

# Headers for authentication
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

# Ensure tmp directory exists
TMP_DIR = "./tmp"
os.makedirs(TMP_DIR, exist_ok=True)


def test_health_check():
    """Test the health check endpoint."""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"Health check failed with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"Cannot connect to server. Make sure it's running on port {PORT}")
        return False
    except Exception as e:
        print(f"Health check error: {e}")
        return False
    return True


def test_simple_html_conversion():
    """Test converting simple HTML to PDF."""
    print("\nTesting simple HTML conversion...")

    html_content = (
        """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Document</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #333; }
            p { line-height: 1.6; }
        </style>
    </head>
    <body>
        <h1>Test PDF Document</h1>
        <p>This is a test document generated from HTML content.</p>
        <p>Generated at: """
        + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        + """</p>
    </body>
    </html>
    """
    )

    payload = {"html": html_content, "options": {"format": "A4", "margin": {"top": "2cm", "right": "2cm", "bottom": "2cm", "left": "2cm"}}}

    try:
        response = requests.post(f"{BASE_URL}/convert", headers=HEADERS, json=payload)

        if response.status_code == 200:
            # Save PDF file
            filename = os.path.join(TMP_DIR, f"test_simple_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"Simple HTML conversion successful - saved as {filename}")
            return True
        else:
            print(f"Simple HTML conversion failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"Simple HTML conversion error: {e}")
        return False


def test_complex_html_conversion():
    """Test converting complex HTML with CSS and tables to PDF."""
    print("\nTesting complex HTML conversion...")

    html_content = (
        """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Complex Test Document</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                max-width: 800px;
                margin: 0 auto;
            }
            h1 {
                color: #4a5568;
                text-align: center;
                border-bottom: 3px solid #667eea;
                padding-bottom: 10px;
            }
            .info-box {
                background: #f7fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            th, td {
                border: 1px solid #e2e8f0;
                padding: 12px;
                text-align: left;
            }
            th {
                background: #edf2f7;
                font-weight: bold;
            }
            .highlight {
                background: #fff5b7;
                padding: 2px 4px;
                border-radius: 3px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Complex PDF Test Document</h1>

            <div class="info-box">
                <h2>Document Information</h2>
                <p><strong>Generated:</strong> """
        + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        + """</p>
                <p><strong>Purpose:</strong> Testing complex HTML to PDF conversion</p>
                <p>This document tests various HTML and CSS features including <span class="highlight">styled text</span>, tables, and layouts.</p>
            </div>

            <h2>Sample Data Table</h2>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Role</th>
                        <th>Department</th>
                        <th>Experience</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>John Doe</td>
                        <td>Senior Developer</td>
                        <td>Engineering</td>
                        <td>5 years</td>
                    </tr>
                    <tr>
                        <td>Jane Smith</td>
                        <td>Product Manager</td>
                        <td>Product</td>
                        <td>3 years</td>
                    </tr>
                    <tr>
                        <td>Mike Johnson</td>
                        <td>Designer</td>
                        <td>Design</td>
                        <td>4 years</td>
                    </tr>
                </tbody>
            </table>

            <h2>Features Tested</h2>
            <ul>
                <li>CSS Grid and Flexbox layouts</li>
                <li>Custom fonts and colors</li>
                <li>Background gradients</li>
                <li>Box shadows and border radius</li>
                <li>Complex table styling</li>
                <li>Text highlighting and formatting</li>
            </ul>
        </div>
    </body>
    </html>
    """
    )

    payload = {
        "html": html_content,
        "options": {"format": "A4", "print_background": True, "margin": {"top": "1cm", "right": "1cm", "bottom": "1cm", "left": "1cm"}},
    }

    try:
        response = requests.post(f"{BASE_URL}/convert", headers=HEADERS, json=payload)

        if response.status_code == 200:
            filename = os.path.join(TMP_DIR, f"test_complex_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"Complex HTML conversion successful - saved as {filename}")
            return True
        else:
            print(f"Complex HTML conversion failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"Complex HTML conversion error: {e}")
        return False


def test_url_conversion():
    """Test converting a URL to PDF."""
    print("\nTesting URL conversion...")

    test_url = "https://httpbin.org/html"

    payload = {"url": test_url, "options": {"format": "A4", "margin": {"top": "1cm", "right": "1cm", "bottom": "1cm", "left": "1cm"}}}

    try:
        response = requests.post(f"{BASE_URL}/convert-url", headers=HEADERS, params=payload)

        if response.status_code == 200:
            filename = os.path.join(TMP_DIR, f"test_url_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"URL conversion successful - saved as {filename}")
            return True
        else:
            print(f"URL conversion failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"URL conversion error: {e}")
        return False


def test_authentication():
    """Test API authentication."""
    print("\nTesting authentication...")

    # Test with wrong API key
    wrong_headers = {"Authorization": "Bearer wrong-api-key", "Content-Type": "application/json"}

    payload = {"html": "<html><body><h1>Test</h1></body></html>"}

    try:
        response = requests.post(f"{BASE_URL}/convert", headers=wrong_headers, json=payload)

        if response.status_code == 401:
            print("Authentication working correctly - rejected wrong API key")
            return True
        else:
            print(f"Authentication test failed - expected 401, got {response.status_code}")
            return False
    except Exception as e:
        print(f"Authentication test error: {e}")
        return False


def main():
    """Run all tests."""
    print("Chromium HTML to PDF Server - API Tests")
    print("=" * 50)

    tests = [test_health_check, test_authentication, test_simple_html_conversion, test_complex_html_conversion, test_url_conversion]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("All tests passed!")
        sys.exit(0)
    else:
        print("Some tests failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
