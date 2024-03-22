VENV_DIR := .venv

install: 
	@echo "root:install"
	@echo "==================="
	python3 -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install -r requirements.txt
	@echo

clean:
	@echo "root:clean"
	@echo "==================="
	rm -rf $(VENV_DIR)
