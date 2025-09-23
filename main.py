import io
import logging
import os
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from playwright.async_api import async_playwright
from pydantic import BaseModel, Field
from pypdf import PdfReader, PdfWriter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Chromium HTML to PDF Server", description="Convert HTML content to PDF using headless Chromium browser", version="1.0.0")

# Security
security = HTTPBearer()

# Environment variables
API_KEY = os.getenv("API_KEY", "your-secret-api-key-here")


# Request models
class HTMLToPDFRequest(BaseModel):
    html: str = Field(..., description="HTML content to convert to PDF")
    options: Optional[dict] = Field(default_factory=dict, description="PDF generation options")
    creator: Optional[str] = Field(None, description="PDF creator metadata field")
    delay: Optional[int] = Field(None, description="Delay in milliseconds before generating PDF (for JS rendering)")
    media: Optional[str] = Field(None, description="Emulate media type (e.g., 'print' or 'screen')")


# PDF options with defaults
DEFAULT_PDF_OPTIONS = {
    "format": "A4",
    "margin": {"top": "1cm", "right": "1cm", "bottom": "1cm", "left": "1cm"},
    "print_background": True,
    "prefer_css_page_size": False,
}


def update_pdf_metadata(pdf_bytes: bytes, creator: Optional[str] = None) -> bytes:
    """Update PDF metadata with custom creator field."""
    if not creator:
        return pdf_bytes

    try:
        # Read the PDF from bytes
        pdf_input = io.BytesIO(pdf_bytes)
        reader = PdfReader(pdf_input)
        writer = PdfWriter()

        # Copy all pages
        for page in reader.pages:
            writer.add_page(page)

        # Update metadata
        metadata = reader.metadata or {}
        writer.add_metadata(
            {
                "/Title": metadata.get("/Title", ""),
                "/Author": metadata.get("/Author", ""),
                "/Subject": metadata.get("/Subject", ""),
                "/Creator": creator,
                "/Producer": metadata.get("/Producer", ""),
                "/Keywords": metadata.get("/Keywords", ""),
            }
        )

        # Write to bytes
        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)
        return output_stream.read()

    except Exception as e:
        logger.warning(f"Failed to update PDF metadata: {e}")
        return pdf_bytes


async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify the API key from the Authorization header."""
    if credentials.credentials != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return credentials.credentials


@app.on_event("startup")
async def startup_event():
    """Install Playwright browsers on startup."""
    logger.info("Installing Playwright browsers...")
    try:
        # Install chromium browser
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            await p.chromium.launch()
        logger.info("Playwright browsers ready")
    except Exception as e:
        logger.error(f"Failed to initialize Playwright: {e}")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Chromium HTML to PDF Server is running"}


@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    try:
        # Test Playwright availability
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            await browser.close()

        return {"status": "healthy", "playwright": "available", "chromium": "ready"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@app.post("/convert", response_class=Response)
async def convert_html_to_pdf(request: HTMLToPDFRequest, api_key: str = Depends(verify_api_key)):
    """
    Convert HTML content to PDF.

    Args:
        request: HTMLToPDFRequest containing HTML content and options
        api_key: API key for authentication

    Returns:
        PDF file as response
    """
    try:
        logger.info("Starting HTML to PDF conversion")

        # Merge user options with defaults
        pdf_options = {**DEFAULT_PDF_OPTIONS, **request.options}

        async with async_playwright() as p:
            # Launch Chromium browser
            browser = await p.chromium.launch(
                headless=True, args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu", "--disable-features=VizDisplayCompositor"]
            )

            try:
                # Create a new page
                page = await browser.new_page()

                # Set viewport for consistent rendering
                await page.set_viewport_size({"width": 1200, "height": 800})

                # Set content and wait for load
                await page.set_content(request.html, wait_until="networkidle")

                # Add delay if specified to allow JavaScript execution
                if request.delay:
                    await page.wait_for_timeout(request.delay)

                # Emulate media type if specified (e.g., 'print' or 'screen')
                if request.media:
                    await page.emulate_media(media=request.media)

                # Generate PDF
                pdf_bytes = await page.pdf(**pdf_options)

                # Update PDF metadata if creator is specified
                if request.creator:
                    pdf_bytes = update_pdf_metadata(pdf_bytes, request.creator)

                logger.info("PDF conversion completed successfully")

                return Response(
                    content=pdf_bytes,
                    media_type="application/pdf",
                    headers={"Content-Disposition": "attachment; filename=converted.pdf", "Content-Type": "application/pdf"},
                )

            finally:
                await browser.close()

    except Exception as e:
        logger.error(f"Error during PDF conversion: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to convert HTML to PDF: {str(e)}")


@app.post("/convert-url", response_class=Response)
async def convert_url_to_pdf(
    url: str,
    options: Optional[dict] = None,
    creator: Optional[str] = None,
    delay: Optional[int] = None,
    media: Optional[str] = None,
    api_key: str = Depends(verify_api_key),
):
    """
    Convert a web page URL to PDF.

    Args:
        url: URL of the web page to convert
        options: PDF generation options
        creator: PDF creator metadata field
        delay: Delay in milliseconds before generating PDF (for JS rendering)
        api_key: API key for authentication

    Returns:
        PDF file as response
    """
    try:
        logger.info(f"Converting URL to PDF: {url}")

        if not url.startswith(("http://", "https://")):
            raise HTTPException(status_code=400, detail="URL must start with http:// or https://")

        # Merge user options with defaults
        pdf_options = {**DEFAULT_PDF_OPTIONS, **(options or {})}

        async with async_playwright() as p:
            # Launch Chromium browser
            browser = await p.chromium.launch(
                headless=True, args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu", "--disable-features=VizDisplayCompositor"]
            )

            try:
                # Create a new page
                page = await browser.new_page()

                # Set viewport for consistent rendering
                await page.set_viewport_size({"width": 1200, "height": 800})

                # Navigate to URL and wait for load
                await page.goto(url, wait_until="networkidle", timeout=30000)

                # Add delay if specified to allow JavaScript execution
                if delay:
                    await page.wait_for_timeout(delay)

                # Emulate media type if specified (e.g., 'print' or 'screen')
                if media:
                    await page.emulate_media(media=media)

                # Generate PDF
                pdf_bytes = await page.pdf(**pdf_options)

                # Update PDF metadata if creator is specified
                if creator:
                    pdf_bytes = update_pdf_metadata(pdf_bytes, creator)

                logger.info("URL to PDF conversion completed successfully")

                return Response(
                    content=pdf_bytes,
                    media_type="application/pdf",
                    headers={"Content-Disposition": "attachment; filename=page.pdf", "Content-Type": "application/pdf"},
                )

            finally:
                await browser.close()

    except Exception as e:
        logger.error(f"Error during URL to PDF conversion: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to convert URL to PDF: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8822))
    uvicorn.run(app, host="0.0.0.0", port=port)
