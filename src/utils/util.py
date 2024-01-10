import os
import chardet
import glob

# Get the absolute path of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the root directory of the GoTFlow project
got_root = os.path.join(current_dir, '../../')

got_root_sign = "${GF_ROOT}"

def read_file(file_path):
    if not file_path:
        print(f"Error: the file_path of {file_path} doesn't exist.")
        return ""

    file_path = file_path.replace(got_root_sign, got_root)

    if not os.path.isfile(file_path):
        print(f"Error: the file_path of {file_path} is not a file.")
        return ""
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    try:
        with open(file_path, 'r', encoding=result['encoding']) as file:
            return file.read()
    except UnicodeDecodeError:
        print(f"Error: Unable to read the file {file_path} with encoding {result['encoding']}")
        return ""


def read_file_list(file_path_regex):
    if not file_path_regex or "${i}" not in file_path_regex:
        print(f"Error: the file_path_regex of {file_path_regex} doesn't exist.")
        return []

    file_path = file_path_regex.replace(got_root_sign, got_root)
    input_file_path = file_path.replace("${i}", "*")

    # Get all text files in the input_dir
    files = glob.glob(input_file_path)
    # Filter out files that start with excluded_prefix
    files_to_merge = [file for file in files]
    # Sort the files by their names
    files_to_merge.sort()

    texts = []
    # Read and merge the contents of the files
    for file in files_to_merge:
        with open(file, 'r') as f:
            texts.append(f.read())
    return texts


def get_output_dir(output_dir_path):
    if not output_dir_path:
        return "."

    output_dir_path = output_dir_path.replace(got_root_sign, got_root)

    if not os.path.exists(output_dir_path):
        os.makedirs(output_dir_path)

    return output_dir_path