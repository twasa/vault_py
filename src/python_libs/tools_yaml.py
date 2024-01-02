from typing import Any

from yaml import load, load_all

from python_libs import tools_fd

try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader

def load_yaml_file(path: str) -> dict[Any,Any]:
    with open(path, 'rb') as f:
        data = load(f.read(), SafeLoader)
    return data

def load_yaml_file_all(path: str) -> list[Any]:
    with open(path, 'rb') as f:
        data = list(load_all(f.read(), SafeLoader))
    return data

def data_load(config_path) -> list[dict[Any, Any]]:
    config_files = tools_fd.recursive_directory_walk(config_path)
    data = []
    for config_file in config_files:
        if config_file.lower().endswith('.yaml') or config_file.lower().endswith('.yml'):
            data.extend(load_yaml_file_all(config_file))
    return data
