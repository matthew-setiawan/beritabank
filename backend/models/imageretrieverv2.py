from serpapi import GoogleSearch
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_first_image_url(query: str) -> str:
    # Get API key from environment
    api_key = os.getenv('SERPAPI_KEY')
    if not api_key:
        raise ValueError("SERPAPI_KEY not found in environment variables")
    
    params = {
        "engine": "google",
        "q": query,
        "tbm": "isch",   # tells Google to search images
        "api_key": api_key
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    
    first_image = results["images_results"][0]["original"]
    return first_image

if __name__ == "__main__":
    print("Testing image retriever v2...")
    try:
        result = get_first_image_url('BNI Siap Optimalkan Dana Rp55 Triliun untuk Dukung Pertumbuhan Ekonomi Nasional')
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
