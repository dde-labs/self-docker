import os
from datetime import datetime
from pathlib import Path

from .utils import foo


def main():
    print(f"Hello {foo()} at {datetime.now():%Y-%m-%d %H:%M:%S}")
    print(os.getenv('CALC_ASAT_DT', 'Not Found!!!'))
    secret_path = Path('/secret')
    if secret_path.exists() and secret_path.is_dir():
        print("Found /secret path")
        print(f"Glob: {list(secret_path.rglob('*'))}")
        for file in secret_path.rglob('*'):
            print(file)
    else:
        print("Does not found /secret path")
