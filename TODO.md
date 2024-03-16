* clean up extractFreqArff.py so that it repeats less code and is callable as a module
* all path checks should be done outside of functions that need a path to speed up the functions that get millions of calls
* have the root makefile call all other make processes 
* add tests in the root makefiile
* setup venvs for whole project. Just do one venv in the root dir to make things simple 
* Do batching instead of a subprocess for each file
* It seems there is a bug in my concurrency code that 
* bug in cleandata.py where if the arff file has no data there is an infinate loop
