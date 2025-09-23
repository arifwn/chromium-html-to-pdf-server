#!/usr/bin/env python3

"""
Python Client Example for Chromium HTML to PDF Server
Demonstrates how to use the PDF conversion API from Python applications
"""

import os
from datetime import datetime
from typing import Any, Dict, Optional

import requests


class PDFConversionClient:
    """Client for interacting with the Chromium HTML to PDF Server API."""

    def __init__(self, base_url: str = "http://localhost:8822", api_key: str = None):
        """
        Initialize the PDF conversion client.

        Args:
            base_url: Base URL of the PDF server
            api_key: API key for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.getenv("API_KEY", "your-secret-api-key-here")
        self.headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    def health_check(self) -> Dict[str, Any]:
        """
        Check if the PDF server is healthy and ready.

        Returns:
            Health status response
        """
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def convert_html_to_pdf(
        self,
        html: str,
        options: Optional[Dict[str, Any]] = None,
        creator: Optional[str] = None,
        delay: Optional[float] = None,
        media: Optional[str] = None,
        output_file: Optional[str] = None,
    ) -> bytes:
        """
        Convert HTML content to PDF.

        Args:
            html: HTML content to convert
            options: PDF generation options
            creator: PDF creator metadata field
            delay: Optional delay in seconds before capturing PDF
            media: Optional media type ('screen' or 'print')
            output_file: Optional file path to save the PDF

        Returns:
            PDF content as bytes
        """
        payload = {"html": html, "options": options or {}}
        if creator:
            payload["creator"] = creator
        if delay is not None:
            payload["delay"] = delay
        if media:
            payload["media"] = media

        response = requests.post(f"{self.base_url}/convert", headers=self.headers, json=payload)
        response.raise_for_status()

        pdf_content = response.content

        if output_file:
            with open(output_file, "wb") as f:
                f.write(pdf_content)
            print(f"PDF saved to: {output_file}")

        return pdf_content

    def convert_url_to_pdf(
        self,
        url: str,
        options: Optional[Dict[str, Any]] = None,
        creator: Optional[str] = None,
        delay: Optional[float] = None,
        media: Optional[str] = None,
        output_file: Optional[str] = None,
    ) -> bytes:
        """
        Convert a web page URL to PDF.

        Args:
            url: URL to convert
            options: PDF generation options
            creator: PDF creator metadata field
            delay: Optional delay in seconds before capturing PDF
            media: Optional media type ('screen' or 'print')
            output_file: Optional file path to save the PDF

        Returns:
            PDF content as bytes
        """
        params = {"url": url, "options": options}
        if creator:
            params["creator"] = creator
        if delay is not None:
            params["delay"] = delay
        if media:
            params["media"] = media

        response = requests.post(f"{self.base_url}/convert-url", headers=self.headers, params=params)
        response.raise_for_status()

        pdf_content = response.content

        if output_file:
            with open(output_file, "wb") as f:
                f.write(pdf_content)
            print(f"PDF saved to: {output_file}")

        return pdf_content


def example_simple_html():
    """Example: Convert simple HTML to PDF."""
    print("Example 1: Simple HTML to PDF")

    client = PDFConversionClient()

    # Check server health
    try:
        health = client.health_check()
        print(f"Server is healthy: {health['status']}")
    except Exception as e:
        print(f"Server health check failed: {e}")
        return

    # Simple HTML content
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Simple Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #2c3e50; border-bottom: 2px solid #3498db; }
            .info { background: #ecf0f1; padding: 20px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>Monthly Report</h1>
        <div class="info">
            <p><strong>Generated:</strong> {{ timestamp }}</p>
            <p><strong>Status:</strong> Active</p>
            <p>This is a sample monthly report generated using the PDF conversion service.</p>
        </div>

        <h2>Summary</h2>
        <ul>
            <li>Total users: 1,234</li>
            <li>Active sessions: 567</li>
            <li>Revenue: $12,345</li>
        </ul>
    </body>
    </html>
    """.replace("{{ timestamp }}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    try:
        # Convert with custom options
        options = {"format": "A4", "margin": {"top": "2cm", "right": "2cm", "bottom": "2cm", "left": "2cm"}, "print_background": True}

        filename = f"simple_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        client.convert_html_to_pdf(html, options=options, creator="PDF Client Example v1.0", delay=1.0, media="print", output_file=filename)

    except Exception as e:
        print(f"Conversion failed: {e}")


def example_invoice_generation():
    """Example: Generate an invoice PDF."""
    print("\nExample 2: Invoice Generation")

    client = PDFConversionClient()

    # Invoice data (in real application, this would come from database)
    invoice_data = {
        "invoice_number": "INV-2024-001",
        "date": datetime.now().strftime("%B %d, %Y"),
        "client": {"name": "Acme Corporation", "address": "123 Business St\nSuite 100\nCity, State 12345"},
        "items": [
            {"description": "Web Development Services", "hours": 40, "rate": 75.00, "amount": 3000.00},
            {"description": "API Integration", "hours": 20, "rate": 85.00, "amount": 1700.00},
            {"description": "Testing & QA", "hours": 15, "rate": 65.00, "amount": 975.00},
        ],
        "subtotal": 5675.00,
        "tax": 567.50,
        "total": 6242.50,
    }

    # Generate invoice HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Invoice {invoice_data["invoice_number"]}</title>
        <style>
            body {{ font-family: 'Helvetica', sans-serif; margin: 0; padding: 40px; color: #333; }}
            .header {{ text-align: center; border-bottom: 2px solid #2c3e50; padding-bottom: 20px; margin-bottom: 30px; }}
            .company {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
            .invoice-info {{ display: flex; justify-content: space-between; margin-bottom: 30px; }}
            .client-info {{ background: #f8f9fa; padding: 20px; border-radius: 8px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #2c3e50; color: white; }}
            .amount {{ text-align: right; }}
            .total-section {{ margin-top: 20px; text-align: right; }}
            .total-row {{ font-weight: bold; font-size: 18px; color: #2c3e50; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="company">Your Company Name</div>
            <p>123 Your Street • Your City, State 12345 • (555) 123-4567</p>
        </div>

        <div class="invoice-info">
            <div>
                <h2>Invoice #{invoice_data["invoice_number"]}</h2>
                <p><strong>Date:</strong> {invoice_data["date"]}</p>
            </div>
            <div class="client-info">
                <h3>Bill To:</h3>
                <p><strong>{invoice_data["client"]["name"]}</strong></p>
                <p>{invoice_data["client"]["address"].replace(chr(10), "<br>")}</p>
            </div>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Description</th>
                    <th>Hours</th>
                    <th>Rate</th>
                    <th class="amount">Amount</th>
                </tr>
            </thead>
            <tbody>
    """

    # Add items
    for item in invoice_data["items"]:
        html += f"""
                <tr>
                    <td>{item["description"]}</td>
                    <td>{item["hours"]}</td>
                    <td>${item["rate"]:.2f}</td>
                    <td class="amount">${item["amount"]:.2f}</td>
                </tr>
        """

    html += f"""
            </tbody>
        </table>

        <div class="total-section">
            <p><strong>Subtotal:</strong> ${invoice_data["subtotal"]:.2f}</p>
            <p><strong>Tax (10%):</strong> ${invoice_data["tax"]:.2f}</p>
            <p class="total-row">Total: ${invoice_data["total"]:.2f}</p>
        </div>

        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd;">
            <p><small>Payment is due within 30 days. Thank you for your business!</small></p>
        </div>
    </body>
    </html>
    """

    try:
        options = {"format": "A4", "margin": {"top": "1cm", "right": "1cm", "bottom": "2cm", "left": "1cm"}}

        filename = f"invoice_{invoice_data['invoice_number']}_{datetime.now().strftime('%Y%m%d')}.pdf"
        client.convert_html_to_pdf(html, options=options, creator="Invoice Generator v2.0", delay=0.5, media="print", output_file=filename)

    except Exception as e:
        print(f"Invoice generation failed: {e}")


def example_url_conversion():
    """Example: Convert a website to PDF."""
    print("\nExample 3: URL to PDF Conversion")

    client = PDFConversionClient()

    # Convert a public website
    url = "https://httpbin.org/html"

    try:
        options = {"format": "A4", "margin": {"top": "1cm", "right": "1cm", "bottom": "1cm", "left": "1cm"}, "print_background": True}

        filename = f"website_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        client.convert_url_to_pdf(url, options=options, creator="Website Archiver v1.5", delay=2.0, media="screen", output_file=filename)

    except Exception as e:
        print(f"URL conversion failed: {e}")


def example_creator_metadata():
    """Example: Demonstrating creator metadata functionality."""
    print("\nExample 4: Creator Metadata Demonstration")

    client = PDFConversionClient()

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Creator Metadata Demo</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .highlight { background-color: #fff3cd; padding: 20px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>PDF Creator Metadata Demo</h1>
        <div class="highlight">
            <p><strong>Note:</strong> This PDF was generated with custom creator metadata.</p>
            <p>Check the PDF properties to see the custom creator field!</p>
        </div>
        <p>Generated at: {{ timestamp }}</p>
    </body>
    </html>
    """.replace("{{ timestamp }}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    try:
        options = {"format": "A4", "margin": {"top": "2cm", "right": "2cm", "bottom": "2cm", "left": "2cm"}}

        filename = f"creator_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        client.convert_html_to_pdf(
            html, options=options, creator="Custom Creator Application v3.0 - Demo Edition", delay=1.5, media="print", output_file=filename
        )
        print("PDF with custom creator metadata saved! Right-click the file and check 'Properties' or 'Document Info' to see the creator field.")

    except Exception as e:
        print(f"Creator metadata demo failed: {e}")


def example_delay_and_media():
    """Example: Demonstrating delay and media parameters."""
    print("\nExample 5: Delay and Media Parameters Demonstration")

    client = PDFConversionClient()

    # HTML with dynamic content that might need time to load
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Delay and Media Demo</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .loading { color: #e74c3c; }
            .loaded { color: #27ae60; display: none; }
            @media screen {
                .screen-only { display: block; color: #3498db; }
                .print-only { display: none; }
            }
            @media print {
                .screen-only { display: none; }
                .print-only { display: block; color: #2c3e50; }
            }
        </style>
        <script>
            setTimeout(function() {
                document.querySelector('.loading').style.display = 'none';
                document.querySelector('.loaded').style.display = 'block';
            }, 1000);
        </script>
    </head>
    <body>
        <h1>Delay and Media Parameters Demo</h1>

        <div class="loading">⏳ Loading dynamic content...</div>
        <div class="loaded">✅ Dynamic content loaded successfully!</div>

        <div class="screen-only">
            <h2>Screen Media</h2>
            <p>This content is only visible when media='screen' is used.</p>
            <p>Perfect for capturing web pages as they appear in browsers.</p>
        </div>

        <div class="print-only">
            <h2>Print Media</h2>
            <p>This content is only visible when media='print' is used.</p>
            <p>Ideal for generating print-optimized documents.</p>
        </div>

        <h2>Delay Parameter Benefits</h2>
        <ul>
            <li>Allows JavaScript to execute and modify content</li>
            <li>Ensures images and fonts are fully loaded</li>
            <li>Gives time for CSS animations to complete</li>
            <li>Waits for AJAX requests to finish</li>
        </ul>
    </body>
    </html>
    """

    try:
        # Example 1: Screen media with delay
        print("  - Generating PDF with screen media and 2-second delay...")
        options = {"format": "A4", "margin": {"top": "2cm", "right": "2cm", "bottom": "2cm", "left": "2cm"}}
        filename_screen = f"delay_media_screen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        client.convert_html_to_pdf(html, options=options, creator="Delay Demo - Screen Media", delay=2.0, media="screen", output_file=filename_screen)

        # Example 2: Print media with delay
        print("  - Generating PDF with print media and 2-second delay...")
        filename_print = f"delay_media_print_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        client.convert_html_to_pdf(html, options=options, creator="Delay Demo - Print Media", delay=2.0, media="print", output_file=filename_print)

        print("  ✅ Generated two PDFs demonstrating different media types:")
        print(f"     - {filename_screen} (screen media)")
        print(f"     - {filename_print} (print media)")
        print("  📝 Compare the files to see the difference between screen and print media!")

    except Exception as e:
        print(f"Delay and media demo failed: {e}")


def main():
    """Run all examples."""
    print("Chromium HTML to PDF Server - Python Client Examples")
    print("=" * 60)

    # Run examples
    example_simple_html()
    example_invoice_generation()
    example_url_conversion()
    example_creator_metadata()
    example_delay_and_media()

    print("\nAll examples completed! Check the generated PDF files.")
    print("Tip: To view PDF metadata, right-click on any PDF file and select 'Properties' or 'Document Info'.")


if __name__ == "__main__":
    # Install required dependency if not available
    try:
        import requests
    except ImportError:
        print("'requests' library is required. Install it with: pip install requests")
        exit(1)

    main()
