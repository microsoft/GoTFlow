@echo off

set "PYTHONPATH=%PYTHONPATH%;src"

:: Get the current date and time
for /f "tokens=2-4 delims=/ " %%a in ("%date%") do set "current_date=%%c%%b%%a"
for /f "tokens=1-2 delims=: " %%a in ("%time%") do set "current_time=%%a%%b"

:: Define the output directory
set "output_dir=data\workflows\MarketPlan\output_%current_date%_%current_time%"

:: Define the directories containing the workflow configuration files
set "directories=data\workflows\MarketPlan\wf_conf\stage_1 data\workflows\MarketPlan\wf_conf\stage_2"

:: Loop over the directories
for %%d in (%directories%) do (
  :: Get a list of all files in the directory
  for /r %%f in (%%d\*) do (
    :: Print the current file path
    echo Processing file: %%f
    :: Run the got_engine.py script with the current file as an argument
    python src/got_engine.py %%f --output_dir %output_dir%
  )
)

:: Run the text_combine.py script
python src/tools/text_combine.py %output_dir%