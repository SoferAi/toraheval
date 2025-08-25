"""
Simple template-based Torah Q&A target for baseline comparison.
"""


def simple_template_response(inputs: dict) -> dict:
    """
    Simple template-based response for baseline comparison.
    
    Args:
        inputs: Dict with 'question' key
        
    Returns:
        Dict with 'answer' key
    """
    question = inputs["question"].lower()
    
    if "divrei yoel" in question or "divrey yoel" in question:
        return {"answer": "This question relates to Divrei Yoel, a collection of Hasidic teachings. I would need to consult the specific text to provide an accurate answer."}
    elif "moses" in question or "moshe" in question:
        return {"answer": "This question concerns Moses (Moshe Rabbenu), the greatest of the prophets and leader of the Jewish people."}
    elif "prayer" in question or "tefillah" in question:
        return {"answer": "This relates to Jewish prayer and spiritual practice. Prayer is a fundamental aspect of Jewish worship."}
    else:
        return {"answer": "This appears to be a Torah-related question that would require careful study of the relevant sources to answer properly."}
