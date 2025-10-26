"""Torah Q&A API Target for LangSmith Evaluation.

This module provides a single API target function that connects to any compatible
server implementation (JavaScript, Python, etc.) for Torah Q&A evaluation.
"""

from http import HTTPStatus

import requests
from langsmith.run_helpers import get_current_run_tree, traceable


@traceable(name="torah_qa_target")
def torah_qa_target(inputs: dict) -> dict:
    """Torah Q&A system that uses an API server.

    This function sends questions to a compatible API server and returns the response.
    The server can be implemented in any language/framework as long as it follows
    the required API interface.

    Args:
        inputs: Dict with 'question' key and optional 'api_url' key

    Returns:
        Dict with 'answer' key and optional metadata

    """
    question = inputs["question"]
    api_url = inputs.get("api_url", "http://localhost:8333/chat")

    try:
        # Get current run tree for distributed tracing
        headers = {"Content-Type": "application/json"}
        if run_tree := get_current_run_tree():
            # Add LangSmith tracing headers for distributed tracing
            headers.update(run_tree.to_headers())

        # Send request to API server
        response = requests.post(
            api_url,
            json={"question": question},
            headers=headers,
            timeout=300,  # 5 minute timeout for Torah Q&A
        )

        if response.status_code == HTTPStatus.OK:
            data = response.json()
            result = {"answer": data["answer"]}

            # Extract any additional metadata if available
            for key in ["sources", "summary",]:
                if key in data:
                    result[key] = data[key]

            # Log sources count for debugging
            sources_count = len(result.get("sources", []))
            print(f"[Target] Received {sources_count} sources from API server")

            return result
        else:
            return {"answer": f"API Error {response.status_code}: {response.text}"}

    except requests.exceptions.ConnectionError:
        return {
            "answer": (
                f"Error: Could not connect to API server at {api_url}. "
                f"Make sure the server is running."
            )
        }
    except requests.exceptions.Timeout:
        return {"answer": "Error: API request timed out (exceeded 5 min.)"}
    except Exception as e:
        return {"answer": f"Error: {str(e)}"}

