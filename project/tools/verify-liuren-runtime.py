"""Verify immutable candidate bytes, module closure, source paragraphs and local links."""
import argparse
import json
from pathlib import Path
from liuren_runtime import verify

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--baseline', type=Path)
    a = p.parse_args()
    print(json.dumps(verify(a.candidate, a.baseline), ensure_ascii=False))
