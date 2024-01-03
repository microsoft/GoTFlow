from flow_nodes import Executor
from utils.aoai import gpt_process_loops
from utils.util import read_file, read_file_list
import os


class RepeatExecutor(Executor):
    def __init__(self, node, llm_string, loops=3):
        super().__init__(node, llm_string, loops)

    def execute(self, output_dir, parameter_cache, output_cache):
        # Call the execute method of the Executor class
        print(f"[Node Id]: {self.node['id']}")

        prompt_template = ""
        parameter_value_dict = {}

        # put all parameters in parameter_cache into parameter_value_dict
        for key, value in parameter_cache.items():
            parameter_value_dict[key] = value

        for parameter in self.node["input_parameters"]:
            name = parameter["name"]
            if parameter["type"] == "prompt_template":
                file_path = parameter["file_path"]
                prompt_template += read_file(file_path)
            elif parameter["type"] == "splitted_prompt_text":
                file_path = parameter["file_path"]
                splitted_contents = read_file_list(file_path)

            elif parameter["type"] == "temp_parameter":
                if name and parameter["value"]:
                    parameter_value_dict[name] = parameter["value"]
            elif parameter["type"] == "output_variable":
                if not name in output_cache:
                    print(f"Error: the value of {name} has not been cached in output_cache.")
                else:
                    parameter_value_dict[parameter["name"]] = output_cache[name]

        if not prompt_template:
            print("Error: There is no prompt template.")
            exit(0)

        prompt = prompt_template

        for key, value in parameter_value_dict.items():
            if not isinstance(value, list):
                key_str = "${" + key.strip() + "}"
                prompt = prompt.replace(key_str, value)

        index = 0
        for content in splitted_contents:
            index += 1
            current_prompt = prompt.replace("${content}", content)

            print(f"[Loop {index}] - [Prompt]: {current_prompt}\n")
            output = gpt_process_loops(self.llm_config, current_prompt, self.loops)
            print(f"[Loop {index}] - [Output]: {output}\n")

            outputs = self.node["output"]

            for output_item in outputs:
                if output and output_item["type"] == "variable":
                    output_cache[output_item["name"]] = output
                elif output and output_item["type"] == "file_list":
                    output_path = os.path.join(output_dir, output_item["name"])
                    output_path = output_path.replace("${i}", str(index))
                    with open(output_path, 'w') as file:
                        file.write(output)

        return