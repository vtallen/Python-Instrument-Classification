VENV_DIR := .venv

install: venv
	$(VENV_DIR)/bin/pip install -r requirements.txt

venv: 
	python3 -m venv $(VENV_DIR)

clean:
	rm -rf $(VENV_DIR)
