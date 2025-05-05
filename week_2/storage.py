import argparse
import json
import os
from pathlib import Path
from typing import Dict, List, Optional


def get_storage_path() -> Path:
    """Return the path to the storage file."""
    return Path(os.path.join(os.getenv('TEMP', '/tmp'), 'storage.data'))


def clear_storage(storage_path: Optional[Path] = None) -> None:
    """Clear the storage file."""
    path = storage_path or get_storage_path()
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def read_data(storage_path: Optional[Path] = None) -> Dict[str, List[str]]:
    """Read and return data from storage file."""
    path = storage_path or get_storage_path()
    if not path.exists():
        return {}

    try:
        with path.open('r') as f:
            content = f.read()
            return json.loads(content) if content else {}
    except (json.JSONDecodeError, IOError):
        return {}


def write_data(data: Dict[str, List[str]], storage_path: Optional[Path] = None) -> None:
    """Write data to storage file."""
    path = storage_path or get_storage_path()
    try:
        with path.open('w') as f:
            json.dump(data, f)
    except IOError as e:
        print(f"Error writing to storage: {e}")


def add_value(key: str, value: str, storage_path: Optional[Path] = None) -> None:
    """Add a value to the storage under the specified key."""
    data = read_data(storage_path)
    data.setdefault(key, []).append(value)
    write_data(data, storage_path)


def get_values(key: str, storage_path: Optional[Path] = None) -> Optional[List[str]]:
    """Retrieve values for a given key from storage."""
    data = read_data(storage_path)
    return data.get(key)


def handle_args() -> None:
    """Parse command line arguments and perform requested actions."""
    parser = argparse.ArgumentParser(description='Key-value storage utility')
    parser.add_argument('--key', help='Key for storage operation')
    parser.add_argument('--val', help='Value to store')
    parser.add_argument('--clear', action='store_true', help='Clear storage')

    args = parser.parse_args()
    storage_path = get_storage_path()

    if args.clear:
        clear_storage(storage_path)
    elif args.key and args.val:
        add_value(args.key, args.val, storage_path)
    elif args.key:
        values = get_values(args.key, storage_path)
        print(', '.join(values) if values else '')
    else:
        parser.print_help()


if __name__ == '__main__':
    handle_args()
