import sys
import os
import types
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
    system_prompt = """
    You are a helpful AI coding agent.

    When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

    - List files and directories

    All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
    """
    schema_get_files_info = types.FunctionDeclaration(
        name="get_files_info",
        description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "directory": types.Schema(
                    type=types.Type.STRING,
                    description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
                ),
            },
        ),
    )
    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
        ]
    )
    try:
        # Send the message list to the model and get a response
        response = client.models.generate_content(
            model='gemini-2.0-flash-001',
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[available_functions],
                system_instruction=system_prompt
                ),
        )
        # Checks for verbose output
        if "--verbose" in sys.argv:
            print(f"User prompt: {user_prompt}")
            print(response.text)
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
        # Prints simple response if verbose is not requested
        elif response.function_calls:
            for item in response.function_calls:
                print(f"Calling function: {item.name}({item.args})")
        else:
            print(response.text)

    except Exception as e:
        # Handle potential errors during the API call
        print(f"An error occurred: {e}")