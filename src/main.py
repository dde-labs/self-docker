import os
from datetime import datetime
from pathlib import Path

from .utils import foo


def main():
    print(f"Hello {foo()} at {datetime.now():%Y-%m-%d %H:%M:%S}")
    print(os.getenv('CALC_ASAT_DT', 'Not Found!!!'))
    print('01) find /secret path')
    secret_path = Path('/secret')
    if secret_path.exists() and secret_path.is_dir():
        print("Found /secret path")
        print(f"Glob: {list(secret_path.rglob('*'))}")
        for file in secret_path.rglob('*'):
            print('-', file)
            if file.is_file():
                file.open(mode='r')
                print(f"Already read file: {file}")
            else:
                print(f"{file} is Directory")
    else:
        print("Does not found /secret path")

    print('-' * 100)
    print('02) find secret path')
    secret_path = Path('secret')
    if secret_path.exists() and secret_path.is_dir():
        print("Found secret path")
        print(f"Glob: {list(secret_path.rglob('*'))}")
        for file in secret_path.rglob('*'):
            print('-', file)
            if file.is_file():
                file.open(mode='r')
                print(f"Already read file: {file}")
            else:
                print(f"{file} is Directory")
    else:
        print("Does not found secret path")
