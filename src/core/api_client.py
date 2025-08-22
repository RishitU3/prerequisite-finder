# ==============================================================================
# File: src/core/api_client.py
#
# This file will contain the core logic for the Gemini API interaction.
# ==============================================================================

import os
import google.generativeai as genai

def configure_gemini(api_key):
    """
    Configures the Gemini API client using the provided API key.

    Args:
        api_key (str): The secret API key to authenticate with the Gemini service.
    """
    try:
        # Manually pass the key directly to the configure function.
        genai.configure(api_key=api_key)
    except Exception as e:
        # This will catch issues with the key, like if it's invalid.
        print(f"Error configuring Gemini API: {e}")

def generate_text(prompt, model_name="gemini-2.5-flash-preview-05-20"):
    """
    Generates text from a given prompt using the specified model.

    Args:
        prompt (str): The text prompt for the model.
        model_name (str): The name of the Gemini model to use.

    Returns:
        str: The generated text from the model, or an error message.
    """
    try:
        model = genai.GenerativeModel(model_name=model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred: {e}"
