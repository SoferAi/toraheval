"""Target function that uses the Anthropic JavaScript API server for Torah Q&A."""

from http import HTTPStatus

import requests
from langsmith.run_helpers import get_current_run_tree, traceable


@traceable(name="anthropic_js_api_target")
def anthropic_js_api_target(inputs: dict) -> dict:
    """Torah Q&A system that uses the Anthropic JavaScript API server.

    This function:
    1. Sends the question to the local JavaScript API server with
       distributed tracing headers
    2. Returns the response from the server using Anthropic API directly

    Args:
        inputs: Dict with 'question' key

    Returns:
        Dict with 'answer' key

    """
    question = inputs["question"]

    try:
        # Get current run tree for distributed tracing
        headers = {"Content-Type": "application/json"}
        if run_tree := get_current_run_tree():
            # Add LangSmith tracing headers for distributed tracing
            headers.update(run_tree.to_headers())

        # Send request to local JavaScript API server
        response = requests.post(
            "http://localhost:8334/chat",
            json={"question": question},
            headers=headers,
            timeout=300,  # 5 minute timeout for Torah Q&A
        )

        if response.status_code == HTTPStatus.OK:
            data = response.json()
            result = {"answer": data["answer"]}

            # Extract usage metadata if available
            if "usage_metadata" in data:
                result["usage_metadata"] = data["usage_metadata"]

            return result
        else:
            return {"answer": f"API Error {response.status_code}: {response.text}"}

    except requests.exceptions.ConnectionError:
        return {
            "answer": (
                "Error: Could not connect to Anthropic JavaScript API server. "
                "Make sure it's running on localhost:8334 (PORT=8334 npm start)"
            )
        }
    except requests.exceptions.Timeout:
        return {"answer": "Error: API request timed out (exceeded 5 min.)"}
    except Exception as e:
        return {"answer": f"Error: {str(e)}"}
