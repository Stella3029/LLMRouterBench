import argparse
import os
import subprocess
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description='Run model connectivity test with explicit cache mode override')
    parser.add_argument('--cache-mode', choices=['redis', 'disabled'], required=True)
    parser.add_argument('--models', nargs='*', default=[])
    parser.add_argument('--config', default='config/data_collector_gpqa_medqa_mmlupro.yaml')
    return parser.parse_args()


def main():
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    env = os.environ.copy()
    env['REDIS_ENABLED'] = 'true' if args.cache_mode == 'redis' else 'false'

    cmd = [sys.executable, 'scripts/test_model_connectivity.py', '--config', args.config]
    if args.models:
        cmd.extend(['--models', *args.models])
    if args.cache_mode == 'disabled':
        cmd.append('--disable-cache')

    print(f"[connectivity-wrapper] cache mode: {args.cache_mode}")
    print(f"[connectivity-wrapper] command: {' '.join(cmd)}")
    raise SystemExit(subprocess.call(cmd, cwd=repo_root, env=env))


if __name__ == '__main__':
    main()
