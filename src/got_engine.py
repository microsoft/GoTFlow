import json
import os.path
import argparse

from flow_nodes import Executor, DecisionMaker
from utils.util import read_file, get_output_dir

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


def process_got_single_parameter_file(flow_items, parameter_cache, llm_string, output_path):
    if output_path and not os.path.exists(output_path):
        os.makedirs(output_path)

    # Create a cache for all nodes
    node_cache = {node['id']: node for node in flow_items}

    # Assume the workflow starts with the first node in the list
    next_nodes_ids = [flow_items[0]['id']]
    processed_nodes_ids = []

    while next_nodes_ids:
        if next_nodes_ids:  # If there are nodes to process
            current_node_id = next_nodes_ids.pop(0)
            current_node = node_cache[current_node_id]
            new_next_nodes_ids = process_node(current_node, llm_string, parameter_cache, output_path)
            processed_nodes_ids.append(current_node_id)
            if new_next_nodes_ids:  # If the current node has next nodes
                next_nodes_ids.extend(node_id for node_id in new_next_nodes_ids if ((node_id not in next_nodes_ids) and (node_id not in processed_nodes_ids)))

    return


def process_got(got_config_path, llm_string):
    # Load the workflow from the JSON configuration file
    with open(got_config_path, encoding="utf8") as f:
        workflow_config = json.load(f)
        if not workflow_config:
            print("Error: The workflow configuration file is empty.")
            exit(0)
        else:
            flow_items = workflow_config['flow_items']
            output_dir = workflow_config['output_dir_path']
            input_parameters = workflow_config['input_parameters']

    output_path = get_output_dir(output_dir)

    if input_parameters and len(input_parameters) > 0:
        for input_parameter in input_parameters:
            suffix = input_parameter['suffix']
            input_parameter_file_path = input_parameter['file_path']

            parameter_cache = {}

            input_parameters_file_content = read_file(input_parameter_file_path)

            if input_parameters_file_content:
                json_obj = json.loads(input_parameters_file_content)
                for key, value in json_obj.items():
                    parameter_cache[key] = value

            if suffix:
                output_path = os.path.join(output_dir, suffix)

            if not os.path.exists(output_path):
                os.makedirs(output_path)

            process_got_single_parameter_file(flow_items, parameter_cache, llm_string, output_path)
    else:
        process_got_single_parameter_file(flow_items, {}, llm_string, output_path)

    return


def get_parameter_file_paths(input_parameter_file_path):
    if not input_parameter_file_path:
        return None

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
    parser.add_argument('--llm_string', default='llm_long', help='Optional string for the llm.')

    args = parser.parse_args()
    workflow_file_path = args.workflow_file_path
    llm_string = args.llm_string  # This will be an empty string if --llm_string is not provided

    process_got(workflow_file_path, llm_string)
