import argparse
import os
from utils.util import read_file

def merge_files(dir_path, file_names, output_path):
    # Check if the directory of the output file exists
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        # If not, create it
        os.makedirs(output_dir)

    # Open the output file
    with open(output_path, 'w', encoding="utf-8") as output_file:
        # Iterate over the file names
        for file_name in file_names:
            # Construct the full file path
            file_path = os.path.join(dir_path, file_name)

            content = read_file(file_path)
            if content:
                output_file.write(content)
                output_file.write("\n\n\n")  # Add a newline character between files

    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Merge files into one.')
    parser.add_argument('source_dir', help='The path to the source dir.')
    parser.add_argument('--output_path', default='DEFAULT', help='Optional string for path to the output file.')

    args = parser.parse_args()
    source_dir = args.source_dir
    output_path = args.output_path

    if not os.path.isdir(source_dir):
        print(f"Error: {source_dir} is not a directory.")
        exit(0)

    if output_path == "DEFAULT":
        output_path = os.path.join(source_dir, "_report.txt")

    merge_files(source_dir, ["introduction.txt", "chapter_1_abstract_outline.txt", "chapter_2_abstract_outline.txt", "chapter_3_abstract_outline.txt", "chapter_4_abstract_outline.txt", "strategy_advice_gtm.txt", "strategy_advice_marketing.txt", "summary.txt"], output_path)