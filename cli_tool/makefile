VENV := ../.venv/

all: venv
	python3 classinst.py -m models/0.1datasetRawModel.pkl flute.mp3

venv:
ifeq ($(wildcard $(VENV)),)
	@echo "venv not installed, installing"
	$(MAKE) -C .. 
else
	@echo "Dependancies already installed."
endif

	. $(VENV)bin/activate

clean:
	rm -r -f audiotmp
