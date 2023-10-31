# CoTFlow: Chain-of-Thought Workflow Engine

This project is an open-source Chain-of-Thought (CoT) workflow engine that parses and executes a CoT workflow. It processes each node in the workflow by executing the associated LLM (Language Learning Model) tasks and determines the subsequent path based on the LLM's output in conditional nodes.

## Features

- Parses and executes a Chain-of-Thought workflow
- Executes LLM tasks for each node in the workflow
- Determines the subsequent path in conditional nodes based on LLM's output
- Caches output variables for use in later nodes
- Supports input parameters from files and output variables
- Outputs results to files or caches them as variables

## Usage

To use the CoT workflow engine, you need to provide a JSON configuration file that defines the workflow and an LLM string for the language learning model.

### Example

```python
llm_string = "AIVertical_short"
cot_config_path = "../data/workflows/Ads/marketing_plan.json"
process_cot(cot_config_path, llm_string)
```

## Configuration

The workflow configuration file is a JSON file that defines the nodes and their properties. Each node has a unique ID, a type (either 'executor' or 'decision_maker'), input parameters, and output properties.

### Node Types

- **Executor**: Executes an LLM task and stores the output in a variable or a file.
- **DecisionMaker**: Evaluates a condition based on the LLM's output and determines the subsequent path in the workflow.

### Input Parameters

Input parameters can be of the following types:

- **output_variable**: A variable that holds the output of a previous node.
- **prompt_template**: A file that contains a template for the LLM task.
- **prompt_parameters**: A file that contains parameters for the LLM task.

### Output Properties

Output properties define how the output of a node should be stored. They can be of the following types:

- **variable**: Stores the output in a variable for use in later nodes.
- **file**: Stores the output in a file.

## Dependencies

To use this project, you need to have the following dependencies installed:

- Python 3.10 or higher
- `utils` module for LLM configuration and GPT processing

## License

This project is open-source and available under the [MIT License](https://opensource.org/licenses/MIT).

# Project

> This repo has been populated by an initial template to help get you started. Please
> make sure to update the content to build a great experience for community-building.

As the maintainer of this project, please make a few updates:

- Improving this README.MD file to provide a great experience
- Updating SUPPORT.MD with content about this project's support experience
- Understanding the security reporting process in SECURITY.MD
- Remove this section from the README

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
