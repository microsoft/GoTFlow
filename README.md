# GoTFlow: Graph-of-Thought Workflow Engine

This project is an open-source Graph-of-Thought (GoT) workflow engine that parses and executes a GoT workflow. It processes each node in the workflow by executing the associated LLM (Language Learning Model) tasks and determines the subsequent path based on the LLM's output in conditional nodes.

The example of this project is provided by Xiaoxu Wang (xiaoxuwang1996@gmail.com) and Jianing Fan (cc.fanjianing@gmail.com). Thanks a lot for our friends Xiaoxu and Jianing.

## Features

- Parses and executes a Graph-of-Thought workflow
- Executes LLM tasks for each node in the workflow
- Determines the subsequent path in conditional nodes based on LLM's output
- Caches output variables for use in later nodes
- Supports input parameters from files and output variables
- Outputs results to files or caches them as variables

## Dependencies

To use this project, you need to have the following dependencies:

- Install Python 3.11 or higher

- Prepare AzureOpenAI Key

  You are required to use your own Azure openai key to access the Azure openai API (AOAI).

  What you need to do is just to put your Azure openai key in a plain text file named openai_key.txt and put it in the conf directory of this project. 

- Run
	```
	pip install -r requirements.txt 
	```
  before run the got_engine.py

- Run
    ```
    set PYTHONPATH=%PYTHONPATH%;src
    ```
  before run the got_engine.py


# Usage

## GoTFlow Engine

The GoTFlow engine is a Python-based workflow engine designed to execute a series of tasks defined in a workflow configuration file. The engine reads the configuration file, processes each task in the order specified, and outputs the results.

To run the GoTFlow engine, use the following command:

```bash
python got_engine.py <workflow_config_file> --output_dir <output_directory> --llm_conf <llm_config_file>
```

Replace <workflow_config_file> with the path to your workflow configuration file. <output_directory> is the directory where the output files will be saved. <llm_config_file> is the path to the LLM configuration file.

Command Line Optional Arguments：

--output_dir: Specifies the directory where the output files will be saved. If not provided, the output directory specified in the workflow configuration file will be used.

--llm_conf: Specifies the path to the LLM configuration file. This file contains the configuration for the Language Learning Model (LLM) used in the workflow.

## Workflow Configuration

A workflow configuration is a JSON file that defines a series of tasks (or "flow items") to be executed by the GoTFlow engine. Each task is represented as an object in the "flow_items" array.

Here is an example of a workflow configuration file:

```json
{
  "output_dir_path": "../data/workflows/MarketPlan/output",
  "input_parameters":[],
  "flow_items":[
  {
    "id": "task1",
    "description": "Description of task1",
    "type": "executor",
    "input_parameters": [],
    "output": [],
    "next_nodes": ["task2"]
  },
  {
    "id": "task2",
    "description": "Description of task2",
    "type": "executor",
    "input_parameters": [],
    "output": [],
    "next_nodes": []
  }
  ]
}
```

### Fields

- `output_dir_path`: The directory where the output files will be saved.
- `input_parameters`: An array of input parameters for the workflow. Each parameter is an object with a `name`, `type`, and `value` or `file_path`.
- `flow_items`: An array of tasks to be executed. Each task is an object with the following fields:
  - `id`: A unique identifier for the task.
  - `description`: A description of the task.
  - `type`: The type of the task. Currently, only "executor" is supported.
  - `input_parameters`: An array of input parameters for the task. Each parameter is an object with a `name`, `type`, and `value` or `file_path`.
  - `output`: An array of output parameters for the task. Each parameter is an object with a `type` and `name`.
  - `next_nodes`: An array of task IDs that should be executed after this task.

### Task Types

Currently, the GoTFlow engine supports the following task types:

- `executor`: Executes a task and produces an output.

### Parameter Types

The GoTFlow engine supports the following parameter types:

- `prompt_template`: A text template used to generate prompts.
- `prompt_text`: A text used as input for a task.
- `prompt_text_list`: A list of texts used as input for a task.
- `temp_parameter`: A temporary parameter used within a task.
- `output_variable`: A variable used to store the output of a task.

For each parameter, you can specify a `value` directly, or provide a `file_path` to a file containing the value.

## Workflow Execution

The GoTFlow engine executes the tasks in the order specified in the "flow_items" array. For each task, the engine reads the input parameters, executes the task, and saves the output parameters. If a task has "next_nodes", the engine will execute those tasks next.

The results of the workflow execution are saved in the directory specified by `output_dir_path`.


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
