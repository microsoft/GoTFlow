from flow_nodes import Executor
from utils.util import read_file, read_file_list
import os
import re


class Splitter(Executor):
    def __init__(self, node):
        super().__init__(node, None )

    def execute(self, output_dir):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for parameter in self.node["input_parameters"]:
            if parameter["type"] == "file" and parameter["name"] == "source_file":
                input_path = parameter["file_path"]
            elif parameter["type"] == "int" and parameter["name"] == "max_length":
                max_length = parameter["value"]

        if not input_path or not max_length:
            print("Error: input_path or max_length is not specified.")
            exit(0)

        outputs = self.node["output"]

        for output_item in outputs:
            if output_item["type"] == "file_list":
                output_file_path = os.path.join(output_dir, output_item["name"])

        content = read_file(input_path)

        paragraphs = self.split_paragraphs(content)
        print(f"Total paragraphs: {len(paragraphs)}")

        current_file = 0
        current_length = 0
        grouped_paragraphs = []

        # Get the folder path
        folder_path = os.path.dirname(output_file_path)
        # Check if the folder exists, if not, create it
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        print(f"max_length: {max_length}")
        if max_length > 0:
            for paragraph in paragraphs:
                paragraph_length = len(paragraph["content"])

                if current_length + paragraph_length + 1 >= max_length:  # +1 是为了考虑换行符
                    # 将当前组合的文本保存到一个新文件中
                    current_file += 1
                    self.print_splited_content(current_file, output_file_path, grouped_paragraphs)

                    current_length = 0
                    grouped_paragraphs = []

                grouped_paragraphs.append(paragraph)
                current_length += paragraph_length + 1

            # 保存最后一个输出文件（如果有内容）
            if len(grouped_paragraphs) > 0:
                current_file += 1
                self.print_splited_content(current_file, output_file_path, grouped_paragraphs)

        elif max_length == 0:
            for paragraph in paragraphs:
                current_file += 1
                self.print_splited_content(current_file, output_file_path, [paragraph])
        elif max_length == -1:
            self.print_splited_content(0, output_file_path, paragraphs)
        else:
            print("Error: max_length is not specified.")
            exit(0)

        return

    def print_splited_content(self, current_file_no, output_file_path, grouped_paragraphs):
        real_output_file_path = output_file_path.replace("${i}", str(current_file_no))
        with open(real_output_file_path, 'w', encoding='utf-8') as output_file:
            for paragraph in grouped_paragraphs:
                output_file.write(paragraph["content"] + '\n')
        return

    def split_paragraphs(self, content):
        code_blocks = re.split(r'(```.*?```)', content, flags=re.DOTALL)
        paragraphs = []
        for block in code_blocks:
            if block.startswith('```') and block.endswith('```'):
                # This is a code block, treat it as a single paragraph
                paragraphs.append({'type': 'code', 'content': block})
            else:
                # This is a non-code block, split it into paragraphs by newline characters
                text_paragraphs = block.split('\n')
                for text_paragraph in text_paragraphs:
                    paragraphs.append({'type': 'text', 'content': text_paragraph})
        return paragraphs

class Merger(Executor):
    def __init__(self, node):
        super().__init__(node, None)

    def execute(self, output_dir):

        for parameter in self.node["input_parameters"]:
            if parameter["type"] == "file_list" and parameter["name"] == "rewritten_data":
                input_file_path = parameter["file_path"]

        merged_content = read_file_list(input_file_path)

        outputs = self.node["output"]

        for output_item in outputs:
            if output_item["type"] == "file":
                output_file_path = os.path.join(output_dir, output_item["name"])

        # Write the merged content to the output_path
        with open(output_file_path, 'w') as f:
            for content in merged_content:
                f.write(content + "\n")

        return