本目录下存储了一系列的工作流配置文件，这些文件共同构成了一个完整的任务，该任务的目标是根据提供的素材撰写营销策略规划报告。

具体的使用方式如下：

1. 按照文件名的顺序，依次将 `wf_conf\stage_1` 和 `wf_conf\stage_2` 目录下的所有工作流配置文件作为参数运行 `src\got_engine.py`。这些配置文件定义了一系列的任务，包括数据处理、模型训练、结果生成等步骤。每个工作流配置文件都可以使用以下命令运行：

```bash
python got_engine.py <workflow_config_file>
```

将 `<workflow_config_file>` 替换为您的工作流配置文件的路径。

2. 在所有的工作流配置文件都正常运行并生成输出后，运行 `src\tools\text_combine.py` 脚本。这个脚本会将所有工作流的输出合并，生成一个名为 `_report.txt` 的文件。这个文件就是整个任务的最终输出。

```bash
python text_combine.py
```

这样，您就可以得到一个完整的营销策略规划报告，该报告是根据您提供的素材自动生成的。

NOTE：GoTFlow 根目录下的 MarketPlan.bat 中已经实现了上面两个步骤的全部操作，Windows 用户直接在 GoTFlow 目录下直接运行 MarketPlan.bat 文件即可自动化实现营销策略规划报告生成的全流程。