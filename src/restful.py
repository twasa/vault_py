import os

import jwt
import python_libs.vault_to_k8s as vault_to_k8s
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
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

def jwt_token_check(request: Request):
    oidc_enabled = os.getenv("oidc_enabled", "false").lower()
    if oidc_enabled == 'true':
        try:
            token = request.headers['x-forwarded-access-token']
            return jwt.decode(token, options={"verify_signature": False}, algorithms=['RS256'])
        except (KeyError, jwt.exceptions.PyJWTError):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing access token.")

@app.get("/_info/")
def info_get():
    return {
        "vault_info": vault_to_k8s.vault_api.info(),
        "k8s_info": vault_to_k8s.k8s_api.get_cluster_info()
    }

@app.post("/resource/")
def resource_create(resource: Resource, request: Request):
    jwt_token_check(request)
    try:
        vault_to_k8s.create_k8s_resource(resource.model_dump())
        return JSONResponse(content={"status": "successful"})
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=f"backend error, reason: {str(e)}")
