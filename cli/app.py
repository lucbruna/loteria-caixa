#!/usr/bin/env python3
import argparse
import subprocess
from pathlib import Path


def run(cmd):
    print('>', cmd)
    subprocess.run(cmd, shell=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('cmd', choices=['audit','predict','report','drift-check'])
    args = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.cmd == 'audit':
        run('python cli/run_audit.py')
    elif args.cmd == 'predict':
        run('python cli/predict.py')
    elif args.cmd == 'report':
        run('python cli/audit_report.py')
    elif args.cmd == 'drift-check':
        run('python src/monitor/drift_simple.py')


if __name__=='__main__':
    main()
