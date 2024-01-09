
import python_libs.vault_to_k8s as vault_to_k8s
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from python_libs import jlogger
from starlette import status

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
    return JSONResponse(
        {
        "vault_info": vault_to_k8s.vault_api.info(),
        "k8s_info": vault_to_k8s.k8s_api.get_cluster_info()
        }
    )

@app.post("/resource/")
def resource_create(resource: Resource):
    try:
        vault_to_k8s.create_k8s_resource(resource.model_dump())
        return JSONResponse(content={"status": "successful"})
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=f"backend error, reason: {str(e)}")

def admission_uid_parse(request_data: dict[str, str]):
    try:
        return request_data['request']['uid']
    except KeyError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="uid not found")

@app.post("/mutate/")
async def mutation(request_data: Request):
    content_type = request_data.headers.get("content-type", None)
    if content_type != "application/json":
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=f"Unsupported media type {content_type}")
    request_dict = await request_data.json()
    logger.info(request_dict)
    uid = admission_uid_parse(request_dict)
    content =  {
        "apiVersion": "admission.k8s.io/v1",
        "kind": "AdmissionReview",
        "response": {
            "uid": uid,
            "allowed": True,
            "status": {"code": 200, "message": "ok"}
        }
    }
    return JSONResponse(content=content)
