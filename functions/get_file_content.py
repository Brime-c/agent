import os

def get_file_content(working_directory, file_path):
    # Safeguard against None or empty file_path
    if not os.path.abspath(os.path.join(working_directory, file_path)).startswith(os.path.abspath(working_directory)):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    elif not os.path.isfile(os.path.join(working_directory, file_path)):
        return f'Error: File not found or is not a regular file: "{file_path}"'
    
    max_characters = 10000
    try:
        with open(os.path.join(working_directory, file_path), 'r') as f:
            file_content_string = f.read()    
    
    except Exception as e:
        return f'Error:{str(e)}'   

    if len(file_content_string) > max_characters:
        truncated_message = f"\n\n[... File {file_path} truncated to {max_characters} characters...]"
        file_content_string = file_content_string[0:10000] + truncated_message
    return file_content_string
        
    