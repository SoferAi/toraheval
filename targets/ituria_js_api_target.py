"""
Target function that uses the local Ituria JavaScript API server for Torah Q&A.
"""
import requests
import json
from typing import Dict

def ituria_js_api_target(inputs: dict) -> dict:
    """
    Torah Q&A system that uses the local JavaScript Ituria API server.
    
    This function:
    1. Sends the question to the local JavaScript API server
    2. Returns the response from the server that uses the same system as ituria
    
    Args:
        inputs: Dict with 'question' key
        
    Returns:
        Dict with 'answer' key
    """
    question = inputs["question"]
    
    try:
        # Send request to local JavaScript API server
        response = requests.post(
            "http://localhost:8000/chat",
            json={"question": question},
            headers={"Content-Type": "application/json"},
            timeout=60  # Longer timeout as it uses multiple tool calls
        )
        
        if response.status_code == 200:
            data = response.json()
            return {"answer": data["answer"]}
        else:
            return {"answer": f"API Error {response.status_code}: {response.text}"}
            
    except requests.exceptions.ConnectionError:
        return {"answer": "Error: Could not connect to Ituria JavaScript API server. Make sure it's running on localhost:8000 (npm start)"}
    except requests.exceptions.Timeout:
        return {"answer": "Error: API request timed out (exceeded 60 seconds)"}
    except Exception as e:
        return {"answer": f"Error: {str(e)}"}
