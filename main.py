import sys
import os
import types
import subprocess
from dotenv import load_dotenv
from google import genai # Keep genai imports together
from google.genai import types # Keep genai imports together
from functions.get_file_content import get_file_content
from functions.get_files_info import get_files_info
from functions.run_python_file import run_python_file
from functions.write_file import write_file

# This block runs only when the script is executed directly
def call_function(function_call_part, verbose=False):
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")
    function_call_part.args["working_directory"] = "./calculator"
    function_map = {
        "get_files_info": get_files_info,
        "get_file_content": get_file_content,
        "write_file": write_file,
        "run_python_file": run_python_file
    }
    
    if function_call_part.name in function_map:
        function_to_call = function_map[function_call_part.name]
        function_result = function_to_call(**function_call_part.args)
    else:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call_part.name,
                    response={"error": f"Unknown function: {function_call_part.name}"},
                )
            ],
        )
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_call_part.name,
                response={"result": function_result},
            )
        ],
    )

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
    - Read file contents
    - Execute Python files with optional arguments
    - Write or overwrite files

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
    schema_get_file_content = types.FunctionDeclaration(
        name="get_file_content",
        description="Reads and returns the contents of a specified file, constrained to the working directory.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="The file_path to read files from, relative to the working directory. If not provided, say that no file_path was provided.",
                ),
            },
        ),
    )
    schema_run_python_file = types.FunctionDeclaration(
        name="run_python_file",
        description="Executes a python file, constrained to the working directory.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="The file_path to execute files from, relative to the working directory. If not provided, say that no file_path was provided.",
                ),
            },
        ),
    )
    schema_write_file = types.FunctionDeclaration(
        name="write_file",
        description="writes content to a file, creating it if it doesn't exist, create file if specified file doesnt exist in the directory, constrained to the working directory.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="The file_path to write content in, relative to the working directory. If not provided, say that no file_path was provided.",
                ),
                "content": types.Schema(
                    type=types.Type.STRING,
                    description="The content to be written in the provided file_path, relative to the working directory. If not provided, say that 'no content was provided'"
                )
            },
        ),
    )
    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_get_file_content,
            schema_run_python_file,
            schema_write_file,
        ]
    )

    iteration = 0
    try:
        while iteration < 20:
            response = client.models.generate_content(
                model='gemini-2.0-flash-001',
                contents=messages,
                config=types.GenerateContentConfig(
                    tools=[available_functions],
                    system_instruction=system_prompt
                    ),
            )
            for candidate in response.candidates:
                messages.append(candidate.content)
                
            
            if response.function_calls:
                for item in response.function_calls:
                    function_call_result = call_function(item, verbose ="--verbose" in sys.argv)
                    if not function_call_result.parts or not function_call_result.parts[0].function_response:
                        raise Exception("There was a fatal Exception")
                    messages.append(function_call_result)
                    if "--verbose" in sys.argv:
                        print(f"-> {function_call_result.parts[0].function_response.response}")
                iteration += 1
                continue
                

            if "--verbose" in sys.argv:
                print(f"User prompt: {user_prompt}")
                print(response.text)
                print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
                print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
            else:
                print(response.text)
            iteration += 1
            break
        
        else:
            print("Maximum iterations reached. Last response:")
            print(response.text)
    except Exception as e:
        # Handle potential errors during the API call
        print(f"An error occurred: {e}")


    
