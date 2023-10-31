import json
import os.path
import argparse

from utils import get_llm_config, gpt_process_loops

output_cache = {}
node_cache = {}


class Executor:
    def __init__(self, node, llm_string, loops=3):
        self.node = node
        self.llm_config = get_llm_config(llm_string)
        self.loops = loops

    def get_value(self, parameter):
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

    def execute(self, output_dir):
        # Here you would put the code to execute the task defined by this node
        print(f"\nExecuting {self.node['id']} ")

        prompt_template = ""
        parameter_value_dict = {}

        for parameter in self.node["input_parameters"]:
            p_value = self.get_value(parameter)
            if parameter["type"] == "prompt_template":
                prompt_template += p_value
            elif parameter["type"] == "prompt_parameters":
                json_obj = json.loads(p_value)
                for key, value in json_obj.items():
                    parameter_value_dict[key] = value
            elif parameter["type"] == "output_variable":
                parameter_value_dict[parameter["name"]] = p_value

        prompt = prompt_template
        for key, value in parameter_value_dict.items():
            if not isinstance(value, list):
                key_str = "${" + key.strip() + "}"
                prompt = prompt.replace(key_str, value)

        output = gpt_process_loops(self.llm_config, prompt, self.loops)
        print(f"Output: {output}\n\n")
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

    def evaluate_simple_condition(self, condition):
        operator = condition['operator']
        operand = condition['operand']
        value = self.get_value(condition['data_source'])

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

    def evaluate_condition(self, condition):
        if condition['is_composed']:
            sub_conditions_results = [
                self.evaluate_condition(sub_condition)
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
            return self.evaluate_simple_condition(condition)

    def decide(self):
        # Here you would put the code to make the decision defined by this node
        print(f"\nDeterming {self.node['id']} ")
        condition = self.node["condition"]
        condition_result = self.evaluate_condition(condition)
        print(f"The result is the condition determine is {condition_result}\n\n")
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


def process_node(node, llm_string, output_dir):

    node_type = node['type']
    next_nodes_ids = None

    if node_type == 'executor':
        executor = Executor(node, llm_string)
        executor.execute(output_dir)
        next_nodes_ids = executor.get_next_node()
    elif node_type == 'decision_maker':
        decision_maker = DecisionMaker(node, llm_string)
        decision_maker.execute(output_dir)
        condition_result = decision_maker.decide()
        next_nodes_ids = decision_maker.get_next_node(condition_result)

    return next_nodes_ids


def process_cot(cot_config_path, llm_string, output_dir="../output"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Load the workflow from the JSON configuration file
    with open(cot_config_path) as f:
        workflow_config = json.load(f)

    # Create a cache for all nodes
    node_cache = {node['id']: node for node in workflow_config}

    # Assume the workflow starts with the first node in the list
    next_nodes_ids = [workflow_config[0]['id']]

    while next_nodes_ids:
        current_node_id = next_nodes_ids.pop(0)
        current_node = node_cache[current_node_id]
        next_nodes_ids.extend(node_id for node_id in process_node(current_node, llm_string, output_dir))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process a workflow based on a configuration file.')
    parser.add_argument('workflow_file_path', help='The path to the workflow configuration file.')
    parser.add_argument('--llm_string', default='', help='Optional string for the llm.')

    args = parser.parse_args()
    workflow_file_path = args.workflow_file_path
    llm_string = args.llm_string  # This will be an empty string if --llm_string is not provided

    if not llm_string:
        llm_string = "AIVertical_short"

    process_cot(workflow_file_path, llm_string)
