# Anthropic Python Server

This is a Python-based API server template for the Torah evaluation system using FastAPI and Anthropic's Claude.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (copy from parent directory or create manually):
```bash
cp ../../.env .env
```

Required environment variables:
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `LANGSMITH_TRACING=true` (optional, for distributed tracing)
- `LANGSMITH_API_KEY`: Your LangSmith API key (optional)

## Running the Server

Start the server on the default port (8334):
```bash
python server.py
```

Or specify a custom port:
```bash
PORT=8335 python server.py
```

## API Endpoints

### POST /chat
Process a Torah Q&A question.

Request body:
```json
{
  "question": "What does the Torah say about kindness?",
  "model": "claude-3-5-sonnet-20241022"  // optional
}
```

Response:
```json
{
  "answer": "The Torah emphasizes kindness (chesed) as a fundamental virtue...",
  "usage_metadata": {
    "input_tokens": 150,
    "output_tokens": 300,
    "total_tokens": 450
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "model_info": {
    "model": "claude-3-5-sonnet-20241022",
    "provider": "anthropic"
  }
}
```

### GET /health
Check server health and configuration.

### GET /
Get server information and available endpoints.

## Testing

Test the API directly:
```bash
curl -X POST http://localhost:8334/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What does the Torah say about kindness?"}'
```

## Distributed Tracing

This server supports LangSmith distributed tracing when:
- `LANGSMITH_TRACING=true` is set
- `LANGSMITH_API_KEY` is configured
- The evaluation framework passes tracing headers

The server will automatically extract trace headers and continue the trace context from the evaluation system.
