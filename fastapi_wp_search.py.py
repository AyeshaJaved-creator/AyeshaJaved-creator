from fastapi import FastAPI, HTTPException
import requests
from base64 import b64encode
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = FastAPI()

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (Adjust in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WordPress REST API endpoint
WORDPRESS_API = "https://www.theedgeroom.com/wp-json/wp/v2/posts"

# Load credentials from environment variables
WORDPRESS_USERNAME = os.getenv("WORDPRESS_USERNAME")
WORDPRESS_APP_PASSWORD = os.getenv("WORDPRESS_APP_PASSWORD")

if not WORDPRESS_USERNAME or not WORDPRESS_APP_PASSWORD:
    raise Exception("❌ ERROR: Missing WordPress credentials in .env file!")

@app.get("/search")
def search(query: str):
    """
    Endpoint to search posts from WordPress based on the provided query.
    Example Usage: http://127.0.0.1:8000/search?query=AI
    """
    if not query:
        raise HTTPException(status_code=400, detail="No search query provided")

    # Encode WordPress credentials in base64
    credentials = f"{WORDPRESS_USERNAME}:{WORDPRESS_APP_PASSWORD}"
    encoded_credentials = b64encode(credentials.encode('utf-8')).decode('utf-8')

    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    try:
        # Send request to WordPress API
        response = requests.get(WORDPRESS_API, params={'search': query}, headers=headers)

        if response.status_code == 200:
            results = response.json()
            
            # Print results in CLI for debugging
            print(f"✅ Search results for '{query}':", results)
            
            return {"results": results}
        else:
            raise HTTPException(status_code=500, detail=f"Failed to fetch posts. Status: {response.status_code}, Response: {response.text}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
