from python_libs import jlogger, k8s, tools_b64, vault

logger = jlogger.Jloger()
vault_api = vault.Vault()
k8s_api = k8s.K8S()

def b64_encoder(vault_data: dict[str, str]) -> dict:
    for key in vault_data:
        vault_data[key] = tools_b64.b64enc(vault_data.get(key))
    return vault_data

def k8s_metadata_build(name: str, config: dict[str, str]):
    return {
        'name': name,
        'namespace': config.get('target_resource_namespace')
    }

def k8s_data_build(config: dict[str, str]):
    data = vault_api.kv2_get(
        config.get('source_kv2_name'),
        config.get('source_kv2_path'),
    )
    if config.get('target_resource_type') == 'secret':
        data = b64_encoder(data)
    return data

def k8s_json_data_combind(manifest_data: dict[str, str]):
    name = manifest_data.get('target_resource_name')
    metadata = k8s_metadata_build(name, manifest_data)
    data = k8s_data_build(manifest_data)
    return {
        "name": name,
        "metadata": metadata,
        "data": data
    }

def create_k8s_resource(manifest_data: dict[str, str]) -> dict[str, str]:
    k8s_json_data = k8s_json_data_combind(manifest_data)
    if manifest_data.get('target_resource_type') == 'secret':
        api_function = getattr(k8s_api, 'secret_create_or_update')
    elif manifest_data.get('target_resource_type') == 'configmap':
        api_function = getattr(k8s_api, 'configmap_create_or_update')
    else:
        raise ValueError('target_resource_type only supported secret or configmap')
    return api_function(**k8s_json_data)
