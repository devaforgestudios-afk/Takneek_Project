import google.generativeai as genai
from PIL import Image
import os
from datetime import datetime
from werkzeug.utils import secure_filename

from brain.config import load_config


config = load_config()


# Gemini API Configuration
my_api_key = config.get('API', 'gemini_api_key', fallback='')
genai.configure(api_key=my_api_key)


def generate(image_path, details_text):
    """Analyzes an image and suggests a fair price"""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
        
        with Image.open(image_path) as img:
            prompt_parts = [
                details_text,
                img,
                "\n\nSee the image and details, and suggest a fair price for the ornament based on recent Indian market trends, satisfying both the maker and supplier. dont ask any follow up questions. and just the price nothing else or any other text. The price should be in INR and rather than a range it should be a single value.The price should match the city trends and no price should be less than 1000 INR and go upto tens of thousands."
            ]
            
            response = model.generate_content(prompt_parts, stream=True)
            generated_price = ""
            for chunk in response:
                generated_price += chunk.text
            
            return generated_price.strip()
    except Exception as e:
        print(f"An error occurred: {e}")
        return "0"
