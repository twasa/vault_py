import json

import jmespath
from python_libs import config, jlogger, tools_http

appconfig = config.Appconfig()
logger = jlogger.Jloger()

class Vault:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.vault_scheme = appconfig.vault_scheme
        self.valult_fqdn = appconfig.vallt_fqdn
        self.vault_uri = f'{self.vault_scheme}://{self.valult_fqdn}'
        self.token = ''
        self.role = ''
        self.policies = []

    def info(self):
        return {
            'uri': self.vault_uri,
            'role': self.role,
            'policies': self.policies
        }

    def auth_approle(self, login_path='/v1/auth/approle/login'):
        json_data = {
            "role_id": appconfig.vault_auth_approle_id,
            "secret_id": appconfig.vault_auth_approle_secret_id,
        }
        url = self.vault_uri + login_path
        r = tools_http.http_put(url=url, json_data=json_data)
        if not r or r.status_code != 200:
            logger.error(f'vault auth failed, reason: {r}')
            return
        response_data = json.loads(r.content)
        self.role = jmespath.search('auth.metadata.role_name', response_data)
        self.policies = jmespath.search('auth.policies', response_data)
        self.token = jmespath.search('auth.client_token', response_data)

    def auth_k8s(self):
        auth_path = appconfig.vault_auth_k8s_path
        login_path = f'/v1/auth/{auth_path}/login'
        url = self.vault_uri + login_path
        json_data = {
            "role": appconfig.vault_auth_k8s_role,
            "jwt": appconfig.vault_auth_k8s_token,
        }
        r = tools_http.http_post(url=url, json_data=json_data)
        if not r or r.status_code != 200:
            logger.error(f'vault auth failed, reason: {r}')
            return
        response_data = json.loads(r.content)
        self.role = jmespath.search('auth.metadata.role', response_data)
        self.policies = jmespath.search('auth.policies', response_data)
        self.token = jmespath.search('auth.client_token', response_data)

    def login(self):
        auth_method_name = appconfig.vault_auth_method_name
        auth_method = getattr(self, f'auth_{auth_method_name}')
        auth_method()

    def sys_status(self) -> bool:
        api_path = '/v1/sys/health'
        url = self.vault_uri + api_path
        headers = {
            'X-Vault-Request': 'true',
            'X-Vault-Token': self.token
        }
        r = tools_http.http_get(url=url, headers=headers)
        if not r:
            return False
        return True

    def kv2_get(self, kv2_mount_path: str, kv2_path: str) -> dict[str, str]:
        if not self.sys_status():
            self.login()
        api_prefix = f'/v1/{kv2_mount_path}/data{kv2_path}'
        url = self.vault_uri + api_prefix
        headers = {
            'X-Vault-Request': 'true',
            'X-Vault-Token': self.token
        }
        r = tools_http.http_get(url=url, headers=headers)
        if not r:
            return
        json_data = json.loads(r.content)
        data = jmespath.search('data.data', json_data)
        return data
