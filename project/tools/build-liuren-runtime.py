"""Build a new immutable local Liuren candidate; never overwrite active skills."""
import argparse
import json
from pathlib import Path
from liuren_runtime import build

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode', choices=['structural', 'enhanced'], required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    m = build(a.output, a.mode)
    print(json.dumps({'mode': m['mode'], 'version': m['version'], 'files': len(m['files'])}))
