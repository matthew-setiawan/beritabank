"""
OpenAI Utilities
Centralized OpenAI API calls for the BeritaBank project
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def call_openai(prompt, model="gpt-3.5-turbo", max_tokens=2000, temperature=0):
    """
    Centralized function to call OpenAI API with fallback logic
    
    Args:
        prompt (str): The prompt to send to OpenAI
        model (str): Model to use (default: "gpt-3.5-turbo")
        max_tokens (int): Maximum tokens to generate (default: 2000)
        temperature (float): Temperature for response randomness (default: 0)
    
    Returns:
        str: The response text from OpenAI, or error message if failed
    """
    try:
        # Get API key from environment
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return "Error: OPENAI_API_KEY not found in environment variables"
        
        client = OpenAI(api_key=api_key)
        
        # Try GPT-5 nano first if specified, fallback to specified model
        if model == "gpt-5-nano":
            try:
                response = client.responses.create(
                    model="gpt-5-nano",
                    input=prompt,
                    temperature=temperature
                )
                return response.output_text
            except:
                # Fallback to chat completions with gpt-3.5-turbo
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.choices[0].message.content.strip()
        elif model.startswith("gpt-5"):
            # GPT-5 family (non-nano) is Responses API-only
            try:
                response = client.responses.create(
                    model=model,
                    input=prompt,
                    temperature=temperature
                )
                return response.output_text
            except Exception:
                # Fallback to gpt-3.5-turbo if GPT-5 fails
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.choices[0].message.content.strip()
        elif model.startswith("o3"):
            # o3 models are Responses API-only
            try:
                response = client.responses.create(
                    model=model,
                    input=prompt,
                    temperature=temperature
                )
                return response.output_text
            except Exception as e:
                # Fallback to gpt-3.5-turbo if o3 fails
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.choices[0].message.content.strip()
        else:
            # Use chat completions for other models (gpt-3.5-turbo, gpt-4, etc.)
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"Error: {str(e)}"
