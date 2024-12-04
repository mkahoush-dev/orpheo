import os

def list_all_files(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list


import os

def merge_files(input_directory, output_file):
    """
    Traverse through all files in the given directory (and subdirectories),
    and merge their content into a single output file.

    Args:
    - input_directory (str): Path to the directory containing files.
    - output_file (str): Path to the output file where contents will be merged.
    """
    # Create or overwrite the output file
    output_file = os.path.join(input_directory, output_file)
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Traverse through the directory and its subdirectories
        for root, dirs, files in os.walk(input_directory):
            for file in files:
                file_path = os.path.join(root, file)
                # Ensure that the file is a regular file (not a directory)
                if os.path.isfile(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            # Write the content of the file into the output file
                            outfile.write(f"\n\n--- Content from {file_path} ---\n\n")
                            outfile.write(infile.read())
                    except Exception as e:
                        print(f"Error reading file {file_path}: {e}")

    print(f"All files merged into {output_file}")



def rename_files_remove_spaces(directory):
    """
    Recursively traverse through a directory and replace spaces with underscores in all filenames.
    
    Args:
        directory (str): Path to the directory to process
    """
    for root, dirs, files in os.walk(directory):
        # First rename directories
        for dir_name in dirs:
            if ' ' in dir_name:
                old_path = os.path.join(root, dir_name)
                new_name = dir_name.replace(' ', '_')
                new_path = os.path.join(root, new_name)
                try:
                    os.rename(old_path, new_path)
                    print(f"Renamed directory: {old_path} -> {new_path}")
                except OSError as e:
                    print(f"Error renaming directory {old_path}: {e}")
        
        # Then rename files
        for file_name in files:
            if ' ' in file_name:
                old_path = os.path.join(root, file_name)
                new_name = file_name.replace(' ', '_')
                new_path = os.path.join(root, new_name)
                try:
                    os.rename(old_path, new_path)
                    print(f"Renamed file: {old_path} -> {new_path}")
                except OSError as e:
                    print(f"Error renaming file {old_path}: {e}")
                    
