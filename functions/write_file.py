import os

def write_file(working_directory, file_path, content):
    # Safeguard against None or empty file_path
    if not os.path.abspath(os.path.join(working_directory, file_path)).startswith(os.path.abspath(working_directory)):
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'

    # if the path_file doesnt exist, write file_path
    elif not os.path.isdir(os.path.join(working_directory, file_path)):
        try:
            with open(os.path.join(working_directory, file_path), 'w') as f:
                f.write(content)
        except Exception as e:
            return f'Error:{str(e)}'
    return f'Succesfully wrote to "{file_path}" ({len(content)} characters written)'