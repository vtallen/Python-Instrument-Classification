VENV := ../.venv/
LOGFILE := output.log

all: venv
	python3 gen_model.py arff models violin trumpet tuba flute chello saxophone | tee $(LOGFILE)

# Check if venv is installed, if not run the makefile in parent dir
venv:
ifeq ($(wildcard $(VENV)),)
	@echo "venv not installed, installing"
	$(MAKE) -C .. 
else
	@echo "Dependancies already installed."
endif
	
	. $(VENV)bin/activate

clean:
	rm -f output.log
	rm -r models
