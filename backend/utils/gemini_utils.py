"""
Gemini Utilities
Centralized Gemini (Google Generative AI) calls for the BeritaBank project
"""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Third-party SDK
import google.generativeai as genai

# Load environment variables
load_dotenv()

def call_gemini(prompt: str,
                model: str = "gemini-1.5-pro",
                temperature: float = 0.0,
                google_search_retrieval: bool = True,
                safety_settings: Optional[Dict[str, Any]] = None) -> str:
    """
    Centralized function to call Gemini models with optional Google Search grounding.

    Args:
        prompt: The prompt to send to Gemini
        model: Gemini model name (default: gemini-1.5-pro)
        temperature: Sampling temperature
        google_search_retrieval: If True, enable Google Search grounding
        safety_settings: Optional safety settings dict to pass through

    Returns:
        str: The response text from Gemini, or error message if failed
    """
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "Error: GEMINI_API_KEY not found in environment variables"

        genai.configure(api_key=api_key)

        # Configure tools (Google Search grounding) if requested
        tools = None
        if google_search_retrieval:
            # GoogleSearchRetrieval currently takes no required fields; pass an empty message
            tools = [
                genai.protos.Tool(
                    google_search_retrieval=genai.protos.GoogleSearchRetrieval()
                )
            ]

        generation_config = {
            "temperature": temperature,
        }
        if safety_settings:
            generation_config.update({"safety_settings": safety_settings})

        # Build the model
        model_client = genai.GenerativeModel(
            model_name=model,
            tools=tools,
            generation_config=generation_config,
        )

        response = model_client.generate_content(prompt)
        # Extract text safely
        if hasattr(response, "text") and response.text:
            return response.text
        if hasattr(response, "candidates") and response.candidates:
            for cand in response.candidates:
                if hasattr(cand, "content") and getattr(cand.content, "parts", None):
                    # Join text parts if present
                    parts = cand.content.parts
                    texts = [getattr(p, "text", "") for p in parts if getattr(p, "text", None)]
                    if texts:
                        return "\n".join(texts)
        return "Error: Empty response from Gemini"

    except Exception as e:
        return f"Error: {str(e)}"
