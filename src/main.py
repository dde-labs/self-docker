from datetime import datetime

from .utils import foo


def main():
    print(f"Hello {foo()} at {datetime.now():%Y-%m-%d %H:%M:%S}")
