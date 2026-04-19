import argparse
import json
from collections import Counter


def main():
    parser = argparse.ArgumentParser(description='Inspect Redis cache hit/miss stats for LLMRouterBench')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=6379)
    parser.add_argument('--password', default='')
    parser.add_argument('--db', type=int, default=0)
    parser.add_argument('--prefix', default='llm-cache')
    args = parser.parse_args()

    import redis

    client = redis.Redis(
        host=args.host,
        port=args.port,
        password=args.password or None,
        db=args.db,
        decode_responses=True,
    )

    info = client.info('stats')
    count = 0
    sample_keys = []
    key_types = Counter()
    for key in client.scan_iter(match=f'{args.prefix}:*', count=200):
        count += 1
        if len(sample_keys) < 20:
            sample_keys.append(key)
        try:
            key_types[client.type(key)] += 1
        except Exception:
            key_types['unknown'] += 1

    payload = {
        'prefix': args.prefix,
        'matching_key_count': count,
        'sample_keys': sample_keys,
        'key_types': dict(key_types),
        'redis_stats': {
            'keyspace_hits': info.get('keyspace_hits', 0),
            'keyspace_misses': info.get('keyspace_misses', 0),
        }
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
