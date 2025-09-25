# Server Templates

This directory contains server templates that can be used with the Torah evaluation system. Each server implements the same API interface but using different technologies or approaches.

## Available Servers

### anthropic-js
JavaScript/Node.js server using Express and Anthropic's JavaScript SDK.
- **Technology**: Node.js, Express, Anthropic JS SDK
- **Port**: 8334 (default)
- **Features**: Distributed tracing, usage metadata tracking

### anthropic-python  
Python server using FastAPI and Anthropic's Python SDK.
- **Technology**: Python, FastAPI, Anthropic Python SDK  
- **Port**: 8334 (default)
- **Features**: Distributed tracing, usage metadata tracking, automatic documentation

## API Interface

All servers implement the same REST API interface:

### POST /chat
Main endpoint for processing Torah Q&A questions.

**Request:**
```json
{
  "question": "What does the Torah say about charity?",
  "model": "claude-3-5-sonnet-20241022"  // optional
}
```

**Response:**
```json
{
  "answer": "The Torah teaches that charity (tzedakah) is...",
  "usage_metadata": {
    "input_tokens": 120,
    "output_tokens": 250,
    "total_tokens": 370
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "anthropic_configured": true,
  "langsmith_configured": true,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### GET /
Server information and available endpoints.

## Running a Server

Each server can be started independently:

```bash
# JavaScript server
cd anthropic-js
PORT=8334 npm start

# Python server  
cd anthropic-python
PORT=8334 python server.py
```

## Using with Evaluation System

The evaluation system uses the generic `api_target` which can connect to any server:

```bash
# Run evaluation using the API target (connects to localhost:8334 by default)
uv run langsmith_evaluation.py api

# Or specify a custom API URL in your code
```

## Creating New Server Templates

To create a new server template:

1. Create a new directory for your server
2. Implement the required API endpoints (`/chat`, `/health`, `/`)
3. Follow the same request/response format
4. Add distributed tracing support using LangSmith headers
5. Include setup instructions in a README.md

## Environment Variables

All servers expect these environment variables:

- `ANTHROPIC_API_KEY`: Your Anthropic API key (required)
- `PORT`: Port to run the server on (default: 8334)
- `LANGSMITH_TRACING`: Enable LangSmith tracing (optional)
- `LANGSMITH_API_KEY`: Your LangSmith API key (optional)

Copy the `.env` file from the project root or create one in each server directory.

## Distributed Tracing

All servers support distributed tracing with LangSmith:
- The evaluation framework passes tracing headers to the server
- Server extracts the headers and continues the trace context
- API calls, tokens, and metadata are tracked within the trace
- No additional configuration needed when both components have LangSmith configured
