* clean up extractFreqArff.py so that it repeats less code and is callable as a module

* have the root makefile call all other make processes 
* Do batching instead of a subprocess for each file
* bug in cleandata.py where if the arff file has no data there is an infinate loop

* Make it so that if normalizedb.py is called in multi mode with 1 thread, it will just call the batch mode function with all of the files 
* Bug in normalizedb.py where if less files than max_processes * numrounds are passed in then no correct commands are generated. See splitaudio.py for fix
* Add docs to normalizedb.py
