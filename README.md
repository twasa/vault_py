# vault-py
vault-py a python implement K8S secret/configmap auto injection and source from Hashicorp Vault

## ecosystems
- K8S API server
- cert-mamager installed and config
- Hashicoro Vault(authentication using AppRole)

## deployment
```shell
git clone git@gitlab.v16cp.me:sre/vault-py.git && cd vault-py
kubectl apply -f k8s_manifests/namespace.yaml
kubectl apply -f k8s_manifests/
```

## how to injection
- update your k8s namespace for add metadata.labels, example as below
```yaml
apiVersion: v1
kind: Namespace
metadata:
    labels:
        vaultpy.io/admission-webhooks: enabled
```

- update your deployment for add annotation, example as below
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: william-test
  namespace: william-labs
spec:
  selector:
    matchLabels:
      app: william-test
  template:
    metadata:
      labels:
        app: william-test
      annotations:
        vaultpy.io/target-resource-name: 'appconfig'
        vaultpy.io/target-resource-type: 'secret'
        vaultpy.io/kv2-name: v16
        vaultpy.io/kv2-path: /stg/HCAdmin
    spec:
      volumes:
        - name: config
          secret:
            secretName: appconfig
      containers:
        - image: ubuntu:22.04
          imagePullPolicy: Always
          name: william-test
          command: ["/bin/sleep", "3650d"]
          volumeMounts:
            - name: config
              readOnly: true
              mountPath: "/app/conf/"
```
