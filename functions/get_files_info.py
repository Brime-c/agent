import os

def get_files_info(working_directory, directory=None):
    # Safeguard
    if directory is None:
        directory = "."

    if not os.path.abspath(os.path.join(working_directory, directory)).startswith(os.path.abspath(working_directory)):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    elif not os.path.isdir(os.path.join(working_directory, directory)):
        return f'Error: "{directory}" is not a directory'

    string_files = []

    try:
        joined_path = os.path.join(working_directory, directory)
        directory_list = os.listdir(joined_path)
    except Exception as e:
        return f'Error:{str(e)}'

    for file in directory_list:
        try:
            file_path = os.path.join(joined_path, file)
        except Exception as e:
            return f'Error:{str(e)}'
            
        try:
            string_files.append(f"- {file}: file_size={os.path.getsize(file_path)} bytes, is_dir={os.path.isdir(file_path)}")
        except Exception as e:
            return f'Error:{str(e)}'

    return "\n".join(string_files)