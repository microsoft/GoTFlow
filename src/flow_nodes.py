from utils.aoai import get_llm_config, gpt_process_loops
from utils.util import read_file
import os

class Executor:
    def __init__(self, node, llm_string, loops=3):
        self.node = node
        self.llm_config = get_llm_config(llm_string)
        self.loops = loops

    def execute(self, output_dir, parameter_cache, output_cache):
        # Here you would put the code to execute the task defined by this node
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
                #if not file_path:
                #    print(f"Error: the file_path of {name} doesn't exist.")
                #    continue
                #with open(file_path, 'r', encoding="utf-8") as file:
                #    prompt_template += file.read()
                prompt_template += read_file(file_path)
            elif parameter["type"] == "prompt_text":
                file_path = parameter["file_path"]
                #if not file_path or not name:
                #    print(f"Error: the file_path of {name} doesn't exist.")
                #    continue
                #with open(file_path, 'r', encoding="utf-8") as file:
                #    prompt_text = file.read()
                prompt_text = read_file(file_path)
                if prompt_text:
                    parameter_value_dict[name] = prompt_text
            elif parameter["type"]  == "prompt_text_list":
                file_paths = parameter["file_paths"]
                if not file_paths or not name:
                    print(f"Error: the file_paths of {name} doesn't exist.")
                    continue
                if not isinstance(file_paths, list):
                    print(f"Error: the file_paths of {name} is not a list.")
                    continue
                prompt_text = ""
                for file_path in file_paths:
                    #with open(file_path, 'r', encoding="utf-8") as file:
                    #    prompt_text += file.read()
                    prompt_text += read_file(file_path)
                parameter_value_dict[name] = prompt_text
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

        print(f"[Prompt]: {prompt}\n")
        output = gpt_process_loops(self.llm_config, prompt, self.loops)
        print(f"[Output]: {output}\n")

        outputs = self.node["output"]

        for output_item in outputs:
            if output and output_item["type"] == "variable":
                output_cache[output_item["name"]] = output
            elif output and output_item["type"] == "file":
                output_path = os.path.join(output_dir, output_item["name"])
                with open(output_path, 'w') as file:
                    file.write(output)
        return

    def get_next_node(self):
        return self.node["next_nodes"]


class DecisionMaker(Executor):
    def __init__(self, node, llm_string, loops=3):
        self.node = node
        self.llm_config = get_llm_config(llm_string)
        self.loops = loops

    def evaluate_simple_condition(self, condition, parameter_cache, output_cache):
        operator = condition['operator']
        operand = condition['operand']
        value = None
        data_source = condition['data_source']
        name = data_source['name']
        if data_source['type'] == "output_variable":
            value = output_cache[name]
        elif data_source['type'] == "input_parameter_file_path":
            value = parameter_cache[name]

        if not value:
            raise ValueError(f'Unknown value of {name}')

        if operator == 'equal':
            return value == operand
        elif operator == 'notequal':
            return value != operand
        elif operator == 'largerthan':
            return value > operand
        elif operator == 'lessthan':
            return value < operand
        elif operator == 'equallargerthan':
            return value >= operand
        elif operator == 'equallessthan':
            return value <= operand
        else:
            raise ValueError(f'Unknown operator: {operator}')

    def evaluate_condition(self, condition, parameter_cache, output_cache):
        if condition['is_composed']:
            sub_conditions_results = [
                self.evaluate_condition(sub_condition, parameter_cache, output_cache)
                for sub_condition in condition['sub_conditions']
            ]
            relation = condition['relation']
            if relation == 'and':
                return all(sub_conditions_results)
            elif relation == 'or':
                return any(sub_conditions_results)
            elif relation == 'not':
                # Assumes that there is exactly one sub-condition
                return not sub_conditions_results[0]
            else:
                raise ValueError(f'Unknown relation: {relation}')
        else:
            return self.evaluate_simple_condition(condition, parameter_cache, output_cache)

    def decide(self, parameter_cache, output_cache):
        # Here you would put the code to make the decision defined by this node
        print(f"")
        condition = self.node["condition"]
        condition_result = self.evaluate_condition(condition, parameter_cache, output_cache)
        print(f"{self.node['id']}: determine next node based on the condition result: {condition_result}\n")
        # For simplicity, return the first path in this example
        return condition_result

    def get_next_node(self, decide_result):
        if decide_result:
            return self.node['forward_paths'][0]['next_nodes']
        else:
            return self.node['forward_paths'][1]['next_nodes']

        for path in self.node['forward_paths']:
            if path['condition_result'] == decide_result:
                return path['next_nodes']
        print(f"Error: condition paths don't cover the result: {decide_result}")
        return []  # return an empty list if no matching path is found
