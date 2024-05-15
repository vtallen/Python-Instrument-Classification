VENV_DIR := .venv

install: 
	@echo "root:install"
	@echo "==================="
	python3 -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install -r requirements.txt
	@echo

all: install
	# Build the dataset
	$(MAKE) -C dataset_gen
	# Move the files to the model gen folder
	cp dataset_gen/arff/* model_gen/arff/

	# Generate a model
	$(MAKE) -C model_gen

	# Move the model to the cli_tool dir
	cp model_gen/models/* .

	# Call the script to compile the cli_tool (should be in root dir)
	
	# Run a test classify using the cli tool

	
	
clean:
	@echo "root:clean"
	@echo "==================="
	rm -rf $(VENV_DIR)
