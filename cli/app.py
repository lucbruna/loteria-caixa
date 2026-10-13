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
    root = Path(__file__).resolve().parents[1].parent
    if args.cmd == 'audit':
        run('python3 loteria-federal-analytica/cli/run_audit.py')
    elif args.cmd == 'predict':
        run('python3 loteria-federal-analytica/cli/predict.py')
    elif args.cmd == 'report':
        run('python3 loteria-federal-analytica/cli/audit_report.py')
    elif args.cmd == 'drift-check':
        run('python3 loteria-federal-analytica/src/monitor/drift_simple.py')


if __name__=='__main__':
    main()
