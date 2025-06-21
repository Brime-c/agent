import os
import subprocess

def run_python_file(working_directory, file_path):
    # Safeguard
    if not os.path.abspath(os.path.join(working_directory, file_path)).startswith(os.path.abspath(working_directory)):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    elif not os.path.isfile(os.path.join(working_directory, file_path)):
        return f'Error: File "{file_path}" not found.'
    elif not os.path.abspath(os.path.join(working_directory, file_path)).endswith(".py"):
        return f'Error: "{file_path}" is not a Python file.'
    try:    
        result = subprocess.run(["python3", file_path], capture_output=True, timeout=30, cwd=working_directory)
        stdout_text = result.stdout.decode()
        stderr_text = result.stderr.decode()
    
        if not stdout_text.strip() and not stderr_text.strip():
            return "No output produced."

        if result.returncode != 0:
            return f"STDOUT: {stdout_text}\nSTDERR: {stderr_text}\nProcess exited with code {result.returncode}"
        
    except Exception as e:
        return f"Error: executing Python file: {e}"    
    return f"STDOUT: {stdout_text}\nSTDERR: {stderr_text}"
