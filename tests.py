from functions.get_files_info import get_files_info

print(get_files_info("calculator", "."))  # Should list files in the current directory
print(get_files_info("calculator", "pkg"))  # Should list files in the pkg directory
print(get_files_info("calculator", "/bin"))  # Should return an error since /bin is outside the working directory
print(get_files_info("calculator", "../"))  # Should return an error since ../ is outside the working directory