import argparse
import os
import subprocess
import sys
from pathlib import Path


DISABLED_VALUES = {"0", "false", "no", "off"}


def parse_args():
    parser = argparse.ArgumentParser(description='Run model connectivity test with default Redis cache or explicit disable mode')
    parser.add_argument('--cache-mode', choices=['default', 'disabled'], default='default')
    parser.add_argument('--models', nargs='*', default=[])
    parser.add_argument('--config', default='config/data_collector_gpqa_medqa_mmlupro.yaml')
    return parser.parse_args()


def main():
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    env = os.environ.copy()

    if args.cache_mode == 'disabled':
        env['REDIS_ENABLED'] = 'false'
        cache_mode_label = 'disabled'
    else:
        if str(env.get('REDIS_ENABLED', '')).strip().lower() in DISABLED_VALUES:
            env.pop('REDIS_ENABLED', None)
        cache_mode_label = 'redis (default runtime config)'

    cmd = [sys.executable, 'scripts/test_model_connectivity.py', '--config', args.config]
    if args.models:
        cmd.extend(['--models', *args.models])
    if args.cache_mode == 'disabled':
        cmd.append('--disable-cache')

    print(f"[connectivity-wrapper] cache mode: {cache_mode_label}")
    print(f"[connectivity-wrapper] command: {' '.join(cmd)}")
    raise SystemExit(subprocess.call(cmd, cwd=repo_root, env=env))


if __name__ == '__main__':
    main()
