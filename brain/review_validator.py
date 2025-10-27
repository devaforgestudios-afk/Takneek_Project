import google.generativeai as genai
from brain.config import load_config

config = load_config()
api_key = config.get('API', 'gemini_api_key', fallback='')

def validate_review(text):
    """
    Analyzes a review to determine if it's appropriate.

    Args:
        text: The review text to analyze.
        api_key: The Gemini API key.

    Returns:
        "good" if the review is appropriate, "bad" otherwise.
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
        prompt = f"Analyze the following review and determine if it contains any inappropriate language, spam, or is otherwise a low-quality review. Respond with 'good' if the review is acceptable and 'bad' if it is not. Review: '{text}'"
        response = model.generate_content(prompt)
        return response.text.strip().lower()
    except Exception as e:
        print(f"An error occurred during review validation: {e}")
        return "bad"