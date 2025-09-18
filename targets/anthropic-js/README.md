# Anthropic JS Target API Server

A standalone JavaScript API server that uses the Anthropic SDK for Torah Q&A evaluation.

## Features

- Uses `@anthropic-ai/sdk` package for direct API connection
- Implements distributed LangSmith tracing for evaluation tracking
- Provides HTTP API endpoint compatible with the evaluation framework
- Supports configurable model selection

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Set up environment variables in `.env`:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   LANGSMITH_TRACING=true
   LANGSMITH_API_KEY=your_langsmith_api_key_here
   PORT=8334
   ```

3. Start the server:
   ```bash
   npm start
   ```
   
   Or for development with auto-restart:
   ```bash
   npm run dev
   ```

## API Endpoints

### POST /chat

Submit a question for Torah Q&A processing.

**Request:**
```json
{
  "question": "What does the Torah say about prayer?",
  "model": "claude-3-5-sonnet-20241022"
}
```

**Response:**
```json
{
  "answer": "The Torah discusses prayer in several contexts...",
  "usage_metadata": {
    "input_tokens": 25,
    "output_tokens": 150,
    "total_tokens": 175
  },
  "timestamp": "2025-01-18T12:00:00.000Z"
}
```

### GET /health

Check server health and configuration status.

### GET /

Server info and available endpoints.

## Distributed Tracing

The server supports distributed tracing through LangSmith:
- Automatically extracts trace headers from incoming requests
- Continues traces from the Python evaluation framework
- Tracks API calls and response metadata for evaluation purposes

## Usage in Evaluation

This server is designed to be used with the `anthropic_js_api` target in the main evaluation framework. The Python target function will make HTTP requests to this server while maintaining distributed tracing context.
