import json
import os.path
import argparse

from flow_nodes import Executor, DecisionMaker

output_cache = {}

def process_node(node, llm_string, output_dir):

    node_type = node['type']
    next_nodes_ids = None

    if node_type == 'executor':
        executor = Executor(node, llm_string)
        executor.execute(output_dir, output_cache)
        next_nodes_ids = executor.get_next_node()
    elif node_type == 'decision_maker':
        decision_maker = DecisionMaker(node, llm_string)
        decision_maker.execute(output_dir, output_cache)
        condition_result = decision_maker.decide(output_cache)
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
    parser.add_argument('--llm_string', default='llm_short', help='Optional string for the llm.')

    args = parser.parse_args()
    workflow_file_path = args.workflow_file_path
    llm_string = args.llm_string  # This will be an empty string if --llm_string is not provided

    process_cot(workflow_file_path, llm_string)
