#!/usr/bin/env python3
"""
Anthropic Python API Server for Torah Q&A Evaluation

This server provides a FastAPI endpoint compatible with the evaluation system.
It can be used as a template for implementing different AI models or approaches.
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import anthropic
from dotenv import load_dotenv
from langsmith import RunTree, traceable
from langsmith.run_helpers import get_current_run_tree

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Anthropic Python Torah Q&A API",
    description="Python server for Torah Q&A using Anthropic Claude",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Anthropic client
anthropic_client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

TORAH_SYSTEM_PROMPT = """
You are a Torah scholar assistant.
Answer questions about Torah texts and sources accurately, providing specific citations
when possible.
If asked about Divrei Yoel or other Hasidic texts, try to provide relevant teachings
and sources.
"""


class ChatRequest(BaseModel):
    question: str
    model: str = "claude-3-5-sonnet-20241022"


class ChatResponse(BaseModel):
    answer: str
    usage_metadata: Dict[str, int]
    timestamp: str
    model_info: Dict[str, str]


@traceable(name="process_torah_question")
def process_torah_question(question: str, model: str = "claude-3-5-sonnet-20241022") -> Dict[str, Any]:
    """Process a Torah question using Anthropic Claude."""
    logger.info(f"Processing question: {question[:100]}...")
    logger.info(f"Using model: {model}")

    try:
        response = anthropic_client.messages.create(
            model=model,
            max_tokens=1000,
            system=TORAH_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": question
                }
            ]
        )

        # Extract the text content from the response
        content = response.content[0]
        answer = content.text if content.type == "text" else str(content)

        # Extract usage metadata
        usage_metadata = {
            "input_tokens": response.usage.input_tokens if response.usage else 0,
            "output_tokens": response.usage.output_tokens if response.usage else 0,
            "total_tokens": (response.usage.input_tokens + response.usage.output_tokens) if response.usage else 0
        }

        logger.info(f"Response generated: {answer[:100]}...")
        logger.info(f"Usage: {usage_metadata['input_tokens']} input, {usage_metadata['output_tokens']} output tokens")

        return {
            "answer": answer.strip(),
            "usage_metadata": usage_metadata,
            "timestamp": datetime.now().isoformat(),
            "model_info": {"model": model, "provider": "anthropic"}
        }
    except Exception as error:
        logger.error(f"Error calling Anthropic API: {error}")
        raise


@app.get("/")
async def root():
    """Root endpoint providing server information."""
    return {
        "message": "Anthropic Python Torah Q&A API Server is running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "chat": "POST /chat",
            "health": "GET /health"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "anthropic_configured": bool(os.getenv("ANTHROPIC_API_KEY")),
        "langsmith_configured": bool(os.getenv("LANGSMITH_TRACING") and os.getenv("LANGSMITH_API_KEY")),
        "timestamp": datetime.now().isoformat()
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, http_request: Request):
    """Process Torah Q&A chat request with distributed tracing support."""
    try:
        if not request.question or not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")

        if not os.getenv("ANTHROPIC_API_KEY"):
            raise HTTPException(status_code=500, detail="Anthropic API key not configured")

        # Extract tracing headers and create/continue trace for distributed tracing
        headers_dict = dict(http_request.headers)
        run_tree = RunTree.from_headers(headers_dict)
        
        # Process the chat request with distributed tracing
        if run_tree:
            # Use the trace context from the evaluation framework
            with run_tree:
                result = process_torah_question(request.question, request.model)
        else:
            # Process without distributed tracing
            result = process_torah_question(request.question, request.model)

        return ChatResponse(**result)

    except HTTPException:
        raise
    except Exception as error:
        logger.error(f"Error processing chat request: {error}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(error)}"
        )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8334))
    
    print(f"🚀 Anthropic Python Torah Q&A API Server starting on http://localhost:{port}")
    print(f"📚 Anthropic API configured: {bool(os.getenv('ANTHROPIC_API_KEY'))}")
    print(f"📊 LangSmith tracing configured: {bool(os.getenv('LANGSMITH_TRACING') and os.getenv('LANGSMITH_API_KEY'))}")
    print(f"📅 Started at: {datetime.now().isoformat()}")
    
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
