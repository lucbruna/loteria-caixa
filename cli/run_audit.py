#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path
from datetime import datetime


def run(cmd, cwd=None):
    print(f"> {cmd}")
    res = subprocess.run(cmd, shell=True, cwd=cwd or Path(__file__).resolve().parents[1].parent)
    return res.returncode


def main():
    root = Path(__file__).resolve().parents[1].parent
    print("="*60)
    print("AUDITORIA COMPLETA - Loteria Federal Analytica")
    print("="*60)
    print(f"Data: {datetime.now().isoformat()}")
    print()
    
    scripts = [
        "python3 loteria-federal-analytica/src/analysis/basic_stats.py",
        "python3 loteria-federal-analytica/src/features/pos_patterns.py",
        "python3 loteria-federal-analytica/src/features/gap.py",
        "python3 loteria-federal-analytica/src/features/sums_ranges.py",
        "python3 loteria-federal-analytica/src/validate/backtest.py",
        "python3 loteria-federal-analytica/src/validate/rolling_backtest.py",
        "python3 loteria-federal-analytica/src/models/intelligent_fast.py",
    ]
    for s in scripts:
        rc = run(s)
        print()
    print("="*60)
    print("AUDITORIA FINALIZADA")
    print("Ver: loteria-federal-analytica/auditoria_completa.md")
    print("Ver: loteria-federal-analytica/README.md")
    print("="*60)


if __name__ == "__main__":
    main()
