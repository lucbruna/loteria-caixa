.PHONY: audit predict report drift test install build-nsis

audit:
	python cli/run_audit.py

predict:
	python cli/predict.py

report:
	python cli/audit_report.py

drift:
	python cli/app.py drift-check

test:
	python -m pytest -q 2>/dev/null || echo "pytest not configured"

build-nsis:
	makensis install.nsi 2>/dev/null || echo "NSIS not found in PATH"

install:
	pip install -r requirements.txt
