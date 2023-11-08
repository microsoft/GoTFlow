import json
import os.path
import argparse

from flow_nodes import Executor, DecisionMaker

output_cache = {}

def process_node(node, llm_string, parameter_cache, output_dir):

    node_type = node['type']
    next_nodes_ids = None

    if node_type == 'executor':
        executor = Executor(node, llm_string)
        executor.execute(output_dir, parameter_cache, output_cache)
        next_nodes_ids = executor.get_next_node()
    elif node_type == 'decision_maker':
        decision_maker = DecisionMaker(node, llm_string)
        decision_maker.execute(output_dir, parameter_cache, output_cache)
        condition_result = decision_maker.decide(parameter_cache, output_cache)
        next_nodes_ids = decision_maker.get_next_node(condition_result)

    return next_nodes_ids


def process_cot(cot_config_path, input_parameter_file_path, llm_string, output_dir="../output"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Load the workflow from the JSON configuration file
    with open(cot_config_path) as f:
        workflow_config = json.load(f)

    parameter_cache = {}
    with open(input_parameter_file_path) as f:
        json_obj = json.load(f)
        for key, value in json_obj.items():
            parameter_cache[key] = value

    # Create a cache for all nodes
    node_cache = {node['id']: node for node in workflow_config}

    # Assume the workflow starts with the first node in the list
    next_nodes_ids = [workflow_config[0]['id']]

    while next_nodes_ids:
        current_node_id = next_nodes_ids.pop(0)
        current_node = node_cache[current_node_id]
        next_nodes_ids.extend(node_id for node_id in process_node(current_node, llm_string, parameter_cache, output_dir))


def get_parameter_file_paths(input_parameter_file_path):
    file_paths = []
    if os.path.isfile(input_parameter_file_path):
        file_paths.append(input_parameter_file_path)
    elif os.path.isdir(input_parameter_file_path):
        # It's a directory, read each .json file
        for filename in os.listdir(input_parameter_file_path):
            if filename.endswith('.json'):
                file_path = os.path.join(input_parameter_file_path, filename)
                file_paths.append(file_path)
    else:
        print(f"{input_parameter_file_path} is neither a file nor a directory.")

    return file_paths

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process a workflow based on a configuration file.')
    parser.add_argument('workflow_file_path', help='The path to the workflow configuration file.')
    parser.add_argument('input_parameter_file_path', help='The path to the input parameter file, or to the folder in which a few input parameter files are.')
    parser.add_argument('--llm_string', default='llm_short', help='Optional string for the llm.')

    args = parser.parse_args()
    workflow_file_path = args.workflow_file_path
    input_parameter_file_path = args.input_parameter_file_path

    file_paths = get_parameter_file_paths(input_parameter_file_path)
    llm_string = args.llm_string  # This will be an empty string if --llm_string is not provided

    for file_path in file_paths:
        print(f"\n\n--- Input Parameter File Path : {file_path} ---")
        process_cot(workflow_file_path, file_path, llm_string)
