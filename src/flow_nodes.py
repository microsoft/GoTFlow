from utils import get_llm_config, gpt_process_loops
import json
import os

class Executor:
    def __init__(self, node, llm_string, loops=3):
        self.node = node
        self.llm_config = get_llm_config(llm_string)
        self.loops = loops

    def get_value(self, parameter, output_cache):
        name = parameter["name"]
        type = parameter["type"]
        if type == "output_variable":
            if not name in output_cache:
                print(f"Error: the value of {name} has not been cached in output_cache.")
            else:
                value = output_cache[name]
                return value
        elif type == "prompt_template" or type == "prompt_parameters":
            file_path = parameter["file_path"]
            if not file_path:
                print(f"Error: the file_path of {name} doesn't exist.")
            with open(file_path, 'r', encoding="utf-8") as file:
                value = file.read()
                return value

        return None

    def execute(self, output_dir, output_cache):
        # Here you would put the code to execute the task defined by this node
        print(f"[Node Id]: {self.node['id']}")

        prompt_template = ""
        parameter_value_dict = {}

        for parameter in self.node["input_parameters"]:
            p_value = self.get_value(parameter, output_cache)
            if parameter["type"] == "prompt_template":
                prompt_template += p_value
            elif parameter["type"] == "prompt_parameters":
                json_obj = json.loads(p_value)
                for key, value in json_obj.items():
                    parameter_value_dict[key] = value
            elif parameter["type"] == "output_variable":
                parameter_value_dict[parameter["name"]] = p_value

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
        if output and self.node["output"]["type"] == "variable":
            output_cache[self.node["output"]["name"]] = output
        elif output and self.node["output"]["type"] == "file":
            output_path = os.path.join(output_dir, self.node["output"]["name"])
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

    def evaluate_simple_condition(self, condition, output_cache):
        operator = condition['operator']
        operand = condition['operand']
        value = self.get_value(condition['data_source'], output_cache)

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

    def evaluate_condition(self, condition, output_cache):
        if condition['is_composed']:
            sub_conditions_results = [
                self.evaluate_condition(sub_condition, output_cache)
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
            return self.evaluate_simple_condition(condition, output_cache)

    def decide(self, output_cache):
        # Here you would put the code to make the decision defined by this node
        print(f"")
        condition = self.node["condition"]
        condition_result = self.evaluate_condition(condition, output_cache)
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
