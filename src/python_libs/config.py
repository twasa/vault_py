import os


class Appconfig:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.in_develop = os.getenv('in_develop', 'false')
        self.annotation_prefix = os.getenv('annotation_prefix', 'vaultpy.io')
        self.kubeconfig = os.getenv('KUBECONFIG')
        self.vault_scheme = os.getenv("vault_scheme")
        self.vallt_fqdn = os.getenv("valult_fqdn")
        self.vault_auth_method_name = os.getenv('VAULT_AUTH_METHOD', 'k8s')
        self.vault_auth_approle_id = os.getenv("role_id")
        self.vault_auth_approle_secret_id  = os.getenv("secret_id")
        self.vault_auth_k8s_path = os.getenv('VAULT_AUTH_K8S_PATH')
        self.vault_auth_k8s_role = os.getenv('VAULT_AUTH_K8S_ROLE')
        if self.in_develop == 'true':
            self.vault_auth_k8s_token = os.getenv('VAULT_AUTH_K8S_TOKEN')
        else:
            with open('/var/run/secrets/kubernetes.io/serviceaccount/token') as sa_token:
                self.vault_auth_k8s_token = sa_token.read()
