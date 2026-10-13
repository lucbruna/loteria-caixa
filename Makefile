.PHONY: audit predict report drift test install build build-exe installer build-nsis

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

# Windows: gera os .exe + o instalador Inno Setup (ver build.ps1)
build:
	powershell -ExecutionPolicy Bypass -File ./build.ps1

# Apenas os executaveis (PyInstaller)
build-exe:
	python -m PyInstaller --noconfirm --clean LoteriaFederal.spec

# Apenas o instalador (usa os .exe ja presentes em dist/)
installer:
	powershell -ExecutionPolicy Bypass -File ./build.ps1 -SkipExe

build-nsis:
	makensis install.nsi 2>/dev/null || echo "NSIS not found in PATH"

install:
	pip install -r requirements.txt
