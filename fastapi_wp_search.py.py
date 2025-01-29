from fastapi import FastAPI, HTTPException
import requests
from base64 import b64encode
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (adjust this in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# WordPress site REST API endpoint
WORDPRESS_API = "https://www.theedgeroom.com/wp-json/wp/v2/posts"

# Your WordPress credentials
WORDPRESS_USERNAME = 'Your Username'  # Replace with your WordPress username
WORDPRESS_APP_PASSWORD = 'Your Password'  # Replace with your WordPress application password

@app.get("/search")
def search(query: str):
    """
    Endpoint to search posts from WordPress based on the provided query.
    Accepts a 'query' parameter to search for posts on WordPress.
    """
    if not query:
        raise HTTPException(status_code=400, detail="No search query provided")
    
    # Fetch search results from WordPress REST API with the query
    params = {'search': query}
    
    # Encode the username and password in base64 format
    credentials = f"{WORDPRESS_USERNAME}:{WORDPRESS_APP_PASSWORD}"
    encoded_credentials = b64encode(credentials.encode('utf-8')).decode('utf-8')
    
    # Set the Authorization header with the base64 encoded credentials
    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    
    try:
        # Send the GET request to WordPress API with the Authorization header
        response = requests.get(WORDPRESS_API, params=params, headers=headers)

        # If the response is successful
        if response.status_code == 200:
            posts = response.json()
            return {"results": posts}  # Return the results to the client
        else:
            raise HTTPException(status_code=500, detail=f"Failed to fetch posts. Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        # Log any exceptions
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
