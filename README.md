# vault-py
vault-py a python implement K8S secret/configmap auto injection and source from Hashicorp Vault

## ecosystems
- K8S API server
- cert-mamager installed and config
- Hashicoro Vault(authentication using AppRole)

## deployment
```shell
git clone git@gitlab.v16cp.me:sre/vault-py.git && cd vault-py
export K8S_ENV=dev
# check resources will be create
kubectl kustomize --load-restrictor LoadRestrictionsNone k8s_manifests/$K8S_ENV
# deploy to k8s
kubectl kustomize --load-restrictor LoadRestrictionsNone k8s_manifests/$K8S_ENV | kubectl apply -f - 
```

## vault server config
```shell
export NAME_SPACE=vault-py
export SA_NAME=vault-py
export SA_SECRET_NAME=vault-py-sa
export K8S_AUTH_ROLE=vault-py
export SA_JWT_TOKEN=$(kubectl -n $NAME_SPACE get secret/$SA_SECRET_NAME --output 'go-template={{ .data.token }}' | base64 --decode)
export CA_CERT=$(kubectl config view --raw --minify --flatten --output='jsonpath={.clusters[].cluster.certificate-authority-data}' | base64 --decode)
export K8S_SERVER=$(kubectl config view --raw --minify --flatten --output='jsonpath={.clusters[].cluster.server}')

# enable k8s auth for k8s cluster
export K8S_AUTH_PATH=example-k8s
vault auth enable --path="$K8S_AUTH_PATH" kubernetes
vault write auth/$K8S_AUTH_PATH/config \
    token_reviewer_jwt="$SA_JWT_TOKEN" \
    kubernetes_host="$K8S_SERVER" \
    kubernetes_ca_cert="$CA_CERT"

# create policy
export VAULT_POLICY=vaultpy-prod
vault policy write $VAULT_POLICY - <<EOF
path "v16/data/prod/*" {
  capabilities = ["read", "list"]
}
path "sys/health" {
  capabilities = ["read"]
}
EOF

# create k8s auth role for k8s cluster
vault write auth/$K8S_AUTH_PATH/role/$K8S_AUTH_ROLE \
    bound_service_account_names=$SA_NAME \
    bound_service_account_namespaces=$NAME_SPACE \
    policies=$VAULT_POLICY \
    ttl=1h
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
  namespace: william-test
spec:
  selector:
    matchLabels:
      app: william-test
  template:
    metadata:
      labels:
        app: william-test
      annotations:
        vaultpy.io/target-resource-type: 'secret'
        vaultpy.io/target-resource-name: 'appconfig'
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
