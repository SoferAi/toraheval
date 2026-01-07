# Torah Evaluation with LangSmith

This project provides a LangSmith evaluation setup for Torah Q&A systems. The system uses a single API-based target that can connect to different server implementations.

## Setup

1. Install dependencies:
```bash
uv sync
```

2. Create `.env` file with your API keys:
```bash
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

## Usage

### List available evaluators:
```bash
uv run langsmith_evaluation.py list
```

### Run evaluation with specific evaluators:
```bash
# Use only correctness and helpfulness evaluators
uv run langsmith_evaluation.py correctness,helpfulness

# Use only Torah-specific evaluators
uv run langsmith_evaluation.py torah_citations,hebrew_handling
```

### Run evaluation with default evaluators:
```bash
uv run langsmith_evaluation.py
```

## Architecture

The evaluation system uses a simple architecture:

- **Single API Target**: The evaluation system makes HTTP requests to a server running on `localhost:8334`
- **Server Templates**: Multiple server implementations are provided in the `servers/` directory
- **Distributed Tracing**: LangSmith tracing headers are passed through for complete visibility

## Server Templates

The `servers/` directory contains different server implementations that all provide the same API interface:

### JavaScript Server (anthropic-js)
```bash
cd servers/anthropic-js
npm install
cp ../../.env .env
PORT=8334 npm start
```

### Python Server (anthropic-python)
```bash
cd servers/anthropic-python
pip install -r requirements.txt
cp ../../.env .env
PORT=8334 python server.py
```

## API Interface

All servers must implement these endpoints:

### POST /chat
Main endpoint for Torah Q&A questions.
```json
// Request
{
  "question": "What does the Torah say about charity?",
  "model": "claude-3-5-sonnet-20241022"
}

// Response
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

### GET /
Server information endpoint.

## Distributed Tracing

The system supports distributed tracing with LangSmith:

- **Trace Continuity**: The evaluation framework passes LangSmith tracing headers to the server
- **Automatic Context**: Servers extract trace headers using `RunTree.from_headers()`
- **Usage Tracking**: API calls, tokens, and response metadata are tracked within the trace context
- **Seamless Integration**: Works automatically when both components have LangSmith configured

This enables complete visibility into the evaluation pipeline across different technologies.

## Evaluators

The system includes several evaluators to comprehensively assess Torah Q&A responses:

### Standard Evaluators:
- **correctness**: Compares output against reference answer (requires ground truth)
- **helpfulness**: Measures how well the response addresses the input question

### Custom Torah-Specific Evaluators:
- **torah_citations**: Checks if responses include proper source citations and follow scholarly conventions
- **hebrew_handling**: Evaluates correct interpretation of Hebrew/Aramaic text and Jewish concepts
- **depth_analysis**: Assesses the depth and sophistication of Torah analysis

## Adding New Server Templates

To add a new server implementation:

1. Create a new directory in `servers/` (e.g., `servers/my-server/`)
2. Implement the required API endpoints (`/chat`, `/health`, `/`)
3. Follow the same request/response format as existing servers
4. Add distributed tracing support using LangSmith headers
5. Include setup instructions in a README.md

The server must implement:
- `POST /chat` - Main Torah Q&A endpoint
- `GET /health` - Health check
- `GET /` - Server information

## Adding New Evaluators

To add a custom evaluator:

1. Open `evaluators.py` 
2. Create a new evaluator function
3. Add it to the `EVALUATOR_FUNCTIONS` registry

Example:
```python
def my_custom_evaluator(inputs: dict, outputs: dict, reference_outputs: dict):
    # Your evaluation logic here
    return {"key": "my_metric", "score": True, "comment": "Good response"}

# Add to registry  
EVALUATOR_FUNCTIONS["my_metric"] = my_custom_evaluator
```

## Dataset

The evaluation uses `Q1-dataset.json` which contains Hebrew Torah scholarship questions and reference answers.

## Testing

You can test the target function before running full evaluations:

```python
# Test the API target (requires server running on localhost:8334)
from targets import torah_qa_target
result = torah_qa_target({'question': 'What is the Jewish view on charity?'})
print(result['answer'])
print(result.get('usage_metadata', 'No usage data'))
```

### Testing Servers Directly

Start any server and test the API directly:

```bash
# Start a server (choose one)
cd servers/anthropic-js && PORT=8334 npm start
# OR
cd servers/anthropic-python && PORT=8334 python server.py

# In another terminal, test the API
curl -X POST http://localhost:8334/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What does the Torah say about kindness?"}'

# Check server health
curl http://localhost:8334/health
```

## Results

After running an evaluation, you'll get a link to view results in the LangSmith UI where you can analyze the Torah Q&A system's performance across different evaluators.
