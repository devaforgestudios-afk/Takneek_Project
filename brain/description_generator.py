import google.generativeai as genai
from PIL import Image

import sys
import os 

from brain.config import load_config


config = load_config()


# Gemini API Configuration
my_api_key = config.get('API', 'gemini_api_key', fallback='')
genai.configure(api_key=my_api_key)

def generate_description(image_path, title, category, material, existing_description=""):
    """Generates a description for an artwork using AI"""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
        
        with Image.open(image_path) as img:
            if existing_description:
                prompt = f"""
                Enhance the following description for an artwork with the given details.
                Make it more evocative and appealing to potential buyers.
                Keep it concise and under 100 words.

                Title: {title}
                Category: {category}
                Material: {material}
                Existing Description: {existing_description}

                Enhanced Description:
                """
            else:
                prompt = f"""
                Write a compelling and brief description (under 80 words) for the following artwork.
                Focus on the visual elements, the craftsmanship, and the potential story behind the piece.
                The description should entice potential buyers and art enthusiasts. 
                The discription is for an ecommerce website made for tradition handicraft artisans and buyers so make the discription according to it only.

                Title: {title}
                Category: {category}
                Material: {material}

                Description:
                """
            
            response = model.generate_content([prompt, img])
            return response.text.strip()
    except Exception as e:
        print(f"An error occurred during description generation: {e}")
        return "Failed to generate description."
