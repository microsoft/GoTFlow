from flow_nodes import Executor
from utils.util import read_file, read_file_list
import os


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

        paragraphs = content.split('\n')

        current_file = 0
        current_length = 0
        current_output = ""

        # Get the output_file_name_root from the input_path
        base_name = os.path.basename(input_path)
        output_file_name_root, _ = os.path.splitext(base_name)

        for paragraph in paragraphs:
            paragraph_length = len(paragraph)
            if current_length + paragraph_length + 1 > max_length:  # +1 是为了考虑换行符
                # 将当前组合的文本保存到一个新文件中
                current_file += 1
                real_output_file_path = output_file_path.replace("${i}", str(current_file))

                with open(real_output_file_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(current_output)

                current_length = 0
                current_output = ""
            else:
                current_output += paragraph + '\n'
                current_length += paragraph_length + 1

        # 保存最后一个输出文件（如果有内容）
        if current_output:
            output_file_path = output_file_path.replace("${i}", str(current_file))
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                output_file.write(current_output)

        return


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