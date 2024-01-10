import os

from python_libs import jlogger

logger = jlogger.Jloger()

class Appconfig:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.in_develop = os.getenv('DEV_MODE', 'false')
        self.annotation_prefix = os.getenv('K8S_ANNOTATION_PREFIX', 'vaultpy.io')
        self.kubeconfig = os.getenv('K8S_CONFIG')
        self.vault_scheme = os.getenv("VAULT_SCHEME")
        self.vallt_fqdn = os.getenv("VAULT_FQDN")
        self.vault_auth_method_name = os.getenv('VAULT_AUTH_METHOD', 'k8s')
        self.vault_auth_approle_id = os.getenv("VAULT_AUTH_APPROLE_ID")
        self.vault_auth_approle_secret_id  = os.getenv("VAULT_AUTH_APPROLE_SECRET_ID")
        self.vault_auth_k8s_path = os.getenv('VAULT_AUTH_K8S_PATH')
        self.vault_auth_k8s_role = os.getenv('VAULT_AUTH_K8S_ROLE')
        if self.in_develop == 'true':
            self.vault_auth_k8s_token = os.getenv('VAULT_AUTH_K8S_TOKEN')
        else:
            try:
                with open('/var/run/secrets/kubernetes.io/serviceaccount/token', 'r') as sa_token:
                    self.vault_auth_k8s_token = sa_token.read()
            except Exception as e:
                logger.error(str(e))
