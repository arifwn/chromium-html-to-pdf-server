# Chromium HTML to PDF Server

A web service that converts HTML content to PDF using a headless Chromium browser. Built with Python, FastAPI, and Playwright for reliable and scalable PDF generation.

## Features

- **Fast & Reliable**: Powered by FastAPI and headless Chromium
- **Secure**: API key authentication
- **Full CSS Support**: Complete styling, fonts, and layout support
- **Responsive**: Handles responsive designs and media queries
- **URL Conversion**: Convert web pages directly from URLs
- **Docker Ready**: Easy deployment with Docker and docker-compose
- **High Performance**: Optimized for concurrent requests
- **Health Monitoring**: Built-in health check endpoints

## Quick Start

### Method 1: Using the Startup Script (Recommended for Development)

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd chromium-html-to-pdf-server
   ```

2. Copy the environment file and configure your API key:
   ```bash
   cp .env.example .env
   # Edit .env and set your API_KEY
   ```

3. Run the startup script:
   ```bash
   ./start.sh
   ```

The script will automatically:
- Create a Python virtual environment
- Install all dependencies
- Install Playwright browsers
- Start the server on port 8822

### Method 2: Manual Setup

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

3. Set environment variables:
   ```bash
   export API_KEY="your-secret-api-key-here"
   export PORT=8822
   ```

4. Run the server:
   ```bash
   python main.py
   ```

### Method 3: Using Docker

1. Build and run with Docker Compose:
   ```bash
   # Edit docker-compose.yml to set your API key
   docker-compose up --build
   ```

2. Or build and run manually:
   ```bash
   docker build -t pdf-server .
   docker run -p 8822:8822 -e API_KEY="your-secret-api-key" pdf-server
   ```

Pre-built images are also available on Docker Hub: `arifwn/chromium-html-to-pdf-server`

## API Documentation

### Authentication

All endpoints require authentication using a Bearer token in the Authorization header:

```bash
curl -H "Authorization: Bearer your-secret-api-key" ...
```

### Endpoints

#### Health Check
```http
GET /health
```

Returns server health status and Playwright availability.

**Response:**
```json
{
  "status": "healthy",
  "playwright": "available",
  "chromium": "ready"
}
```

#### Convert HTML to PDF
```http
POST /convert
Content-Type: application/json
Authorization: Bearer your-api-key
```

**Request Body:**
```json
{
  "html": "<html><body><h1>Hello World</h1></body></html>",
  "options": {
    "format": "A4",
    "margin": {
      "top": "1cm",
      "right": "1cm",
      "bottom": "1cm",
      "left": "1cm"
    },
    "print_background": true
  }
}
```

**Response:** PDF file (application/pdf)

#### Convert URL to PDF
```http
POST /convert-url
Authorization: Bearer your-api-key
```

**Parameters:**
- `url` (string): URL to convert
- `options` (object, optional): PDF generation options

**Response:** PDF file (application/pdf)

### PDF Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `format` | string | "A4" | Paper format (A4, A3, A5, Letter, etc.) |
| `margin` | object | `{"top": "1cm", "right": "1cm", "bottom": "1cm", "left": "1cm"}` | Page margins |
| `print_background` | boolean | `true` | Include background graphics |
| `prefer_css_page_size` | boolean | `false` | Use CSS page size |

## Usage Examples

### cURL Examples

**Simple HTML conversion:**
```bash
curl -X POST "http://localhost:8822/convert" \
  -H "Authorization: Bearer your-secret-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<html><body><h1>Hello PDF!</h1></body></html>",
    "options": {"format": "A4"}
  }' \
  --output document.pdf
```

**URL conversion:**
```bash
curl -X POST "http://localhost:8822/convert-url" \
  -H "Authorization: Bearer your-secret-api-key" \
  -d "url=https://example.com" \
  -d "options={\"format\":\"A4\"}" \
  --output webpage.pdf
```

### Python Client

Use the included Python client for easy integration:

```python
from client_example import PDFConversionClient

# Initialize client
client = PDFConversionClient(
    base_url="http://localhost:8822",
    api_key="your-secret-api-key"
)

# Convert HTML to PDF
html = "<html><body><h1>Hello World</h1></body></html>"
pdf_bytes = client.convert_html_to_pdf(
    html=html,
    options={"format": "A4"},
    output_file="output.pdf"
)

# Convert URL to PDF
pdf_bytes = client.convert_url_to_pdf(
    url="https://example.com",
    options={"format": "A4"},
    output_file="webpage.pdf"
)
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');
const fs = require('fs');

const convertHtmlToPdf = async (html, options = {}) => {
  try {
    const response = await axios.post('http://localhost:8822/convert', {
      html: html,
      options: options
    }, {
      headers: {
        'Authorization': 'Bearer your-secret-api-key',
        'Content-Type': 'application/json'
      },
      responseType: 'arraybuffer'
    });

    fs.writeFileSync('output.pdf', response.data);
    console.log('PDF generated successfully!');
  } catch (error) {
    console.error('Error:', error.response.data);
  }
};

// Usage
const html = '<html><body><h1>Hello from Node.js!</h1></body></html>';
convertHtmlToPdf(html, { format: 'A4' });
```

## Testing

Run the included test suite to verify functionality:

```bash
# Make sure the server is running first
python test_api.py
```

Or run the Python client examples:

```bash
python client_example.py
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_KEY` | Secret key for API authentication | `"your-secret-api-key-here"` |
| `PORT` | Server port | `8822` |
| `LOG_LEVEL` | Logging level | `"INFO"` |

### PDF Default Options

The server uses these default PDF options (can be overridden per request):

```python
{
    "format": "A4",
    "margin": {
        "top": "1cm",
        "right": "1cm",
        "bottom": "1cm",
        "left": "1cm"
    },
    "print_background": True,
    "prefer_css_page_size": False
}
```

## Performance Optimization

- **Concurrent Requests**: The server handles multiple PDF generation requests concurrently
- **Browser Reuse**: Chromium instances are efficiently managed by Playwright
- **Memory Management**: Each conversion uses a fresh browser context
- **Resource Limits**: Configure appropriate memory and CPU limits in production

## Production Deployment

### Docker Deployment

```bash
# Build production image
docker build -t pdf-server:latest .

# Run with environment variables
docker run -d \
  --name pdf-server \
  -p 8822:8822 \
  -e API_KEY="your-production-api-key" \
  -e LOG_LEVEL="WARNING" \
  --restart unless-stopped \
  pdf-server:latest
```

### Health Monitoring

Monitor the service using the health check endpoint:

```bash
curl http://localhost:8822/health
```

Set up monitoring tools to check this endpoint regularly.

### Security Considerations

1. **API Key Management**: Use strong, unique API keys and rotate them regularly
2. **Network Security**: Deploy behind a reverse proxy (nginx, Apache)
3. **Rate Limiting**: Implement rate limiting to prevent abuse
4. **Input Validation**: Be cautious with untrusted HTML content
5. **Resource Limits**: Set appropriate memory and timeout limits

## Troubleshooting

### Common Issues

**Server won't start:**
- Check if port 8822 is available
- Verify Python and pip are installed
- Ensure all dependencies are installed

**PDF generation fails:**
- Check Playwright browser installation: `playwright install chromium`
- Verify system dependencies are installed
- Check server logs for detailed error messages

**Authentication errors:**
- Verify API key is set correctly
- Check Authorization header format: `Bearer your-api-key`

**Docker issues:**
- Ensure Docker has sufficient memory (recommend 2GB+)
- Check container logs: `docker logs pdf-server`

### Debugging

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python main.py
```

Check system requirements:

```bash
# Test Playwright installation
python -c "
from playwright.async_api import async_playwright
import asyncio

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        print('Chromium available!')
        await browser.close()

asyncio.run(test())
"
```

## Development

### Project Structure

```
chromium-html-to-pdf-server/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── start.sh               # Development startup script
├── test_api.py            # API test suite
├── client_example.py      # Python client examples
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose setup
├── .env.example           # Environment variables template
└── README.md              # This file
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python test_api.py`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or contributions, please open an issue on the project repository.
