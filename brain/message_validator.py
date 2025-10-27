import google.generativeai as genai 
from brain.config import load_config

config = load_config()
api_key = config.get('API', 'gemini_api_key', fallback='')


def validate_message(text):
    """
    Analyzes a message to determine if it's appropriate.
    Args:
        text: Dictionary containing 'name', 'subject', and 'message'.
    Returns:
        "good" if the message is appropriate, "bad" otherwise.
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
        
        # Format the dictionary data properly
        prompt = f"""Analyze the following contact form submission and determine if it is a random message, spam, or contains any inappropriate language. Respond with ONLY 'good' if the message is acceptable and 'bad' if it is not.

Name: {text.get('name', '')}
Subject: {text.get('subject', '')}
Message: {text.get('message', '')}"""
        
        response = model.generate_content(prompt)
        result = response.text.strip().lower()
        
        # Ensure we only get 'good' or 'bad'
        if 'good' in result:
            return 'good'
        else:
            return 'bad'
            
    except Exception as e:
        print(f"An error occurred during message validation: {e}")
        return "bad"  # Fail closed for safety