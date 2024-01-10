from typing import Any

from kubernetes import client, config
from python_libs import config as app_conf
from python_libs import jlogger

appconfig = app_conf.Appconfig()
logger = jlogger.Jloger()


class K8S(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        in_develop = appconfig.in_develop
        if in_develop.lower() == 'true':
            logger.info("in develop mode...")
            try:
                k8s_config = config.load_kube_config(config_file=appconfig.kubeconfig)
            except Exception as e:
                logger.error(str(e))
                return
        else:
            config.load_incluster_config()
            k8s_config = None
        self.api_client = client.ApiClient(configuration=k8s_config)
        self.coreapi = client.CoreV1Api(api_client=self.api_client)

    def get_cluster_info(self):
        if response := self.coreapi.read_namespaced_config_map(name='cluster-info', namespace='kube-system'):
            data = response.data
        return{ "cluster": data}

    def pod_list(self):
        logger.info("Listing pods with their IPs:")
        ret = self.coreapi.list_pod_for_all_namespaces(watch=False)
        for pod_obj in ret.items:
            logger.info("%s\t%s\t%s" %
                (
                    pod_obj.status.pod_ip,
                    pod_obj.metadata.namespace,
                    pod_obj.metadata.name
                )
            )

    def secret_get(self, name:str, namespace: str) -> bool:
        try:
            self.coreapi.read_namespaced_secret(name=name, namespace=namespace)
            return True
        except Exception as e:
            logger.error(str(e))
            return False

    def secret_create_or_update(self, name: str, metadata: dict[Any, Any], data: dict[Any, Any]):
        namespace = metadata['namespace']
        body = client.V1Secret(
            api_version="v1",
            kind="Secret",
            metadata=client.V1ObjectMeta(**metadata),
            data=data,
            # string_data=string_data,
            type='Opaque'
        )
        if self.secret_get(name=name, namespace=namespace):
            return self.coreapi.patch_namespaced_secret(
                name=name,
                namespace=namespace,
                body=body,
                pretty='true'
            )
        else:
            return self.coreapi.create_namespaced_secret(
                namespace=namespace,
                body=body,
                pretty='true'
            )

    def configmap_get(self, name: str, namespace: str) -> bool:
        try:
            self.coreapi.read_namespaced_config_map(name=name, namespace=namespace)
            return True
        except Exception as e:
            logger.error(str(e))
            return False

    def configmap_create_or_update(self, name: str, metadata: dict[Any, Any], data: dict[Any, Any]):
        namespace = metadata['namespace']
        body = client.V1ConfigMap(
            api_version="v1",
            kind="ConfigMap",
            metadata=client.V1ObjectMeta(**metadata),
            data=data,
        )

        if self.configmap_get(name=name, namespace=namespace):
            return self.coreapi.patch_namespaced_config_map(
                name=name,
                namespace=namespace,
                body=body,
                pretty='true'
            )
        else:
            return self.coreapi.create_namespaced_config_map(
                namespace=namespace,
                body=body,
                pretty='true'
            )
