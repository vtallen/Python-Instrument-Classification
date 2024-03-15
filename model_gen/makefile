LOGFILE := output.log

all: 
	python3 gen_model.py arff models violin trumpet tuba flute chello saxophone | tee $(LOGFILE)

clean:
	rm -f output.log
	rm -r models
