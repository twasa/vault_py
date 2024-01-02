import json
import os

import jmespath
from python_libs import jlogger, tools_http

logger = jlogger.Jloger()

class Vault:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.vault_scheme = os.getenv("vault_scheme")
        self.valult_fqdn = os.getenv("valult_fqdn")
        self.vault_uri = f'{self.vault_scheme}://{self.valult_fqdn}'
        self.token = ''
        self.role = ''
        self.policies = []
        self.login_with_approle()

    def info(self):
        return {
            'uri': self.vault_uri,
            'role': self.role,
            'policies': self.policies
        }

    def login_with_approle(self, login_path='/v1/auth/approle/login'):
        json_data = {
            "role_id": os.getenv("role_id"),
            "secret_id": os.getenv("secret_id"),
        }
        url = self.vault_uri + login_path
        r = tools_http.http_put(url=url, json_data=json_data)
        if not r or r.status_code != 200:
            logger.error(f'vault auth failed, reason: {r}')
            return
        response_data = json.loads(r.content)
        self.role = response_data['auth']['metadata']['role_name']
        self.policies = response_data['auth']['policies']
        self.token = jmespath.search('auth.client_token', response_data)

    def kv2_get(self, kv2_mount_path, kv2_path) -> dict[str, str]:
        headers = {
            'X-Vault-Request': 'true',
            'X-Vault-Token': self.token
        }
        api_prefix = f'/v1/{kv2_mount_path}/data'
        url = self.vault_uri + api_prefix + kv2_path
        r = tools_http.http_get(url=url, headers=headers)
        if not r:
            return
        json_data = json.loads(r.content)
        data = jmespath.search('data.data', json_data)
        return data
