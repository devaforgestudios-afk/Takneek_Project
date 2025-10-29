from openai import OpenAI
from PIL import Image
import os, base64
from brain.config import load_config

from datetime import datetime

def edit_image_with_traditional_background(image_path: str, output_dir: str, prompt: str = None):
    """
    Edits an image using OpenAI's gpt-image-1 model to add a traditional Indian-style background.
    
    Args:
        image_path (str): Path to the input image.
        output_dir (str): Directory to save the enhanced image.
        prompt (str, optional): Custom prompt for the image edit.
    
    Returns:
        str: Path to the edited image (if saved locally) or URL if available.
    """
    # Load config and API key
    config = load_config()
    api_key = config.get('API', 'openai_api_key', fallback='').strip()
    client = OpenAI(api_key=api_key)

    if not prompt:
        prompt = "Give the product a traditional Indian e-commerce styled background — elegant, decorative, and vibrant, while keeping the product clear and centered."

    # Convert to PNG
    png_path = os.path.splitext(image_path)[0] + "_converted.png"
    try:
        img = Image.open(image_path).convert("RGBA")
        img.save(png_path, format="PNG")
    except Exception as e:
        raise RuntimeError(f"Error converting image: {e}")

    try:
        # Edit image using GPT Image Model
        with open(png_path, "rb") as img_file:
            response = client.images.edit(
                model="gpt-image-1",
                image=img_file,
                prompt=prompt
            )

        # Handle the response
        result = None
        if hasattr(response.data[0], "url") and response.data[0].url:
            result = response.data[0].url
            print("Edited image URL:", result)
        elif hasattr(response.data[0], "b64_json") and response.data[0].b64_json:
            image_data = base64.b64decode(response.data[0].b64_json)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S%f')
            output_filename = f"enhanced_{timestamp}.png"
            output_path = os.path.join(output_dir, output_filename)
            
            with open(output_path, "wb") as f:
                f.write(image_data)
            result = output_path
            print("Edited image saved locally at:", output_path)
        else:
            print("No edited image returned.")
            result = None

    except Exception as e:
        raise RuntimeError(f"Image editing failed: {e}")
    
    finally:
        # Clean up temporary PNG
        if os.path.exists(png_path):
            os.remove(png_path)
            print("Temporary PNG deleted.")

    return result


