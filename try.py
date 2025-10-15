import os
import google.generativeai as genai
from PIL import Image

def generate(image_path, details_text):
    """
    Analyzes an image of an ornament and suggests a fair price.
    """
    try:
        # Configure the API key from environment variables
        api_key = "AIzaSyAlv3bdC2r3dAW7dL_5mZumkElQVXmN2Yk"
        if not api_key:
            print("Error: GOOGLE_API_KEY environment variable not set.")
            return
        genai.configure(api_key=api_key)

        # Load the image
        img = Image.open(image_path)

        # Initialize the generative model
        model = genai.GenerativeModel('gemini-2.5-flash-lite')

        # Create the prompt
        prompt_parts = [
            details_text,
            img,
            "\n\nSee the image and details, and suggest a fair price for the ornament based on recent Indian market trends, satisfying both the maker and supplier. dont ask any follow up questions. and just the price nothing else or any other text. The price should be in INR and rather than a range it should be a single value."
        ]

        # Generate content and stream the response
        response = model.generate_content(prompt_parts, stream=True)

        print("--- AI Generated Output ---")
        for chunk in response:
            print(chunk.text, end="")
        print("\n--------------------------")

    except FileNotFoundError:
        print(f"Error: The file was not found at {image_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    generate(
        "C:\\Users\\HP\\Documents\\takneev5\\static\\uploads\\artworks\\20251015_161948_vase.jpg",
        "This is a handcrafted gold-plated necklace with semi-precious stones."
    )