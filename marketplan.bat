@echo off

set "PYTHONPATH=%PYTHONPATH%;src"

:: Define the directories containing the workflow configuration files
set "directories=data\workflows\MarketPlan\wf_conf\stage_1 data\workflows\MarketPlan\wf_conf\stage_2"

:: Loop over the directories
for %%d in (%directories%) do (
  :: Get a list of all files in the directory
  for /r %%f in (%%d\*) do (
    :: Print the current file path
    echo Processing file: %%f
    :: Run the got_engine.py script with the current file as an argument
    python src/got_engine.py %%f
  )
)

:: Run the text_combine.py script
python src/tools/text_combine.py "data\workflows\MarketPlan\output"