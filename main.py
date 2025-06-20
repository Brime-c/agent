import sys
import os
from dotenv import load_dotenv
from google import genai # Keep genai imports together
from google.genai import types # Keep genai imports together

# This block runs only when the script is executed directly
if __name__ == "__main__":
    # Ensure the user provides a command-line argument for the prompt
    if len(sys.argv) < 2:
        print("Usage: python main.py \"Your prompt here\"")
        sys.exit(1) # Exit if no prompt is provided

    # Capture the user's prompt from the command line arguments
    user_prompt = sys.argv[1]

    # Prepare the message in the format expected by the API
    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]

    # Load environment variables from a .env file
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")

    # Check if the API key was loaded
    if not api_key:
        print("Error: GEMINI_API_KEY not found. Make sure your .env file is set up.")
        sys.exit(1)

    # Initialize the Google Generative AI client
    client = genai.Client(api_key=api_key)

    try:
        # Send the message list to the model and get a response
        response = client.models.generate_content(
            model='gemini-2.0-flash-001', contents=messages,
        )
        # Checks for verbose output
        if "--verbose" in sys.argv:
            print(f"User prompt: {user_prompt}")
            print(response.text)
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
        # Prints simple response if verbose is not requested
        else:
            print(response.text)

    except Exception as e:
        # Handle potential errors during the API call
        print(f"An error occurred: {e}")