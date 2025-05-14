import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")

def check_rate_limit():
    """Check the rate limit for the Mistral API using raw HTTP requests."""
    url = "https://api.mistral.ai/v1/chat/completions"  # Replace with the actual Mistral API endpoint
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "open-mistral-7b",
        "messages": [{"role": "user", "content": "Test rate limit"}]
    }

    try:
        # Make the API request
        response = requests.post(url, headers=headers, json=payload)

        # Check if the request was successful
        if response.status_code == 200:
            print("Request successful. You are within the rate limit.")
        elif response.status_code == 429:
            print("Rate limit exceeded!")

        # Extract and print rate limit headers
        print(f"X-RateLimit-Limit: {response.headers.get('X-RateLimit-Limit', 'Unknown')}")
        print(f"X-RateLimit-Remaining: {response.headers.get('X-RateLimit-Remaining', 'Unknown')}")
        print(f"X-RateLimit-Reset: {response.headers.get('X-RateLimit-Reset', 'Unknown')}")
        print(f"Retry-After: {response.headers.get('Retry-After', 'Unknown')} seconds")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    check_rate_limit()