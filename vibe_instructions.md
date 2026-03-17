+ For all testing and running of code use the `.venv` environment
+ When creating new test scripts, occasionally move older ones to the `tests` folder, even if that breaks path dependencies. We will keep older test scripts in this folder as some kind of backup and keep the root folder clean.
+ The output of test scripts should also go in the `tests` folder.
+ Scripts starting with `SCRIPT_` are my way to indicate scripts that will be used for a specific task
+ If you write documentation, place the files in the `docs` folder
+ The `docs` folder contains a `yaml` file documenting the `mistralai` api and a file `mistral_examples.md` which contains an md version of the webpage of Mistral documenting agent handoffs.
+ The folder also contains the `mistralai` api code (it's not installed in the `.venv` this enables you to directly inspect the API code, if needed).


**Don't write any code until we have discussed things.**


