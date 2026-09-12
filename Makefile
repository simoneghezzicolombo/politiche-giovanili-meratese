PYTHON ?= python

help:
	@echo "1) Inserisci i file ufficiali in data/raw/"
	@echo "2) make openbdap OPENBDAP=data/raw/<file>"
	@echo "3) make istat ISTAT=data/raw/<file>"
	@echo "4) make dataset"

openbdap:
	$(PYTHON) scripts/01_openbdap.py --input "$(OPENBDAP)"

istat:
	@if [ -n "$(ISTAT)" ]; then $(PYTHON) scripts/02_istat_population.py --input "$(ISTAT)" --year 2024; else $(PYTHON) scripts/02_istat_population.py --year 2024; fi

dataset:
	$(PYTHON) scripts/03_build_dataset.py
	$(PYTHON) scripts/05_audit_low_values.py
	$(PYTHON) scripts/06_figures.py
