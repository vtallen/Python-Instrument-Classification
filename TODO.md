* Add documentation to normalizedb.py
* Check all files for needed documentation
* Make it so that all scripts assume a / on the back of output dirs, this is inconsistant right now
* clean up extractFreqArff.py so that it repeats less code and is callable as a module
* all path checks should be done outside of functions that need a path to speed up the functions that get millions of calls
