from pydantic import BaseModel


class VaultpyConfig(BaseModel):
    name: str
    target_resource_name: str
    target_resource_namespace: str
    target_resource_type: str
    source_kv2_name: str
    source_kv2_path: str
