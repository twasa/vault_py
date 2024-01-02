import python_libs.vault_to_k8s as vault_to_k8s
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from python_libs import jlogger

logger = jlogger.Jloger()

app = FastAPI()

class Resource(BaseModel):
    name: str
    target_resource_name: str
    target_resource_namespace: str
    target_resource_type: str
    source_kv2_name: str
    source_kv2_path: str

@app.get("/_info/")
def info_get():
    return {
        "vault_info": vault_to_k8s.vault_api.info(),
        "k8s_info": vault_to_k8s.k8s_api.get_cluster_info()
    }

@app.post("/resource/")
def resource_create(resource: Resource):
    try:
        vault_to_k8s.create_k8s_resource(resource.model_dump())
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=f"backend error, reason: {str(e)}")
    return {"status": "success"}
