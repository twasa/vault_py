import json
from typing import Any


def load_json_file(path: str) -> dict:
    with open(path, 'rb') as f:
        json_data = json.loads(f.read())
        return json_data

def json_data_serialization(json_data: dict[Any, Any]):
    return json.dumps(json_data)

def json_data_deserialization(data):
    return json.loads(data)
