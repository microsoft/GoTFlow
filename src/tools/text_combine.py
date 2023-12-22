import os


def merge_files(dir_path, file_names, output_path):
    # Open the output file
    with open(output_path, 'w') as output_file:
        # Iterate over the file names
        for file_name in file_names:
            # Construct the full file path
            file_path = os.path.join(dir_path, file_name)
            # Open and read the file
            with open(file_path, 'r') as input_file:
                content = input_file.read()
                # Write the content to the output file
                output_file.write(content)
                output_file.write("\n\n\n")  # Add a newline character between files


if __name__ == "__main__":
    output_dir = "../../data/workflows/MarketPlan/output/"
    merge_files(output_dir, ["introduction.txt", "chapter_1_abstract_outline.txt", "chapter_2_abstract_outline.txt", "chapter_3_abstract_outline.txt", "chapter_4_abstract_outline.txt", "strategy_advice_gtm.txt", "strategy_advice_marketing.txt", "summary.txt"], "../../data/workflows/MarketPlan/output/_report.txt")