from basemodels.vaultpy import VaultpyConfig
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from python_libs import config, flows, jlogger
from starlette import status

logger = jlogger.Jloger()

app = FastAPI()
appconfig = config.Appconfig()


@app.get("/_info")
def info_get():
    return JSONResponse(
        {
            "vault_info": flows.vault_api.info(),
            "k8s_info": flows.k8s_api.get_cluster_info(),
        }
    )


@app.post("/resource")
def resource_create(vault_config: VaultpyConfig):
    try:
        flows.create_k8s_resource(vault_config.model_dump())
        return JSONResponse(content={"status": "successful"})
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=f"backend error, reason: {str(e)}")


def content_validation(request_data: Request):
    content_type = request_data.headers.get("content-type", "None")
    if content_type != "application/json":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported media type {content_type}",
        )


def admission_uid_parse(request_data: dict[str, str]):
    try:
        return request_data["request"]["uid"]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="uid not found"
        )


def annotation_data_parse(request_data: dict[str, str]) -> dict:
    annotation_data = {}
    annotation_prefix = appconfig.annotation_prefix
    try:
        annotation_data_raw = request_data["request"]["object"]["metadata"][
            "annotations"
        ]
        annotation_data["target_resource_namespace"] = request_data["request"][
            "namespace"
        ]
        annotation_data["target_resource_name"] = annotation_data_raw[
            f"{annotation_prefix}/target-resource-name"
        ]
        annotation_data["target_resource_type"] = annotation_data_raw[
            f"{annotation_prefix}/target-resource-type"
        ]
        annotation_data["source_kv2_name"] = annotation_data_raw[
            f"{annotation_prefix}/kv2-name"
        ]
        annotation_data["source_kv2_path"] = annotation_data_raw[
            f"{annotation_prefix}/kv2-path"
        ]
        return annotation_data
    except KeyError as e:
        logger.error(str(e))
        return {}


def admission_resource_create(request_dict: dict[str, str]):
    if annotation_data := annotation_data_parse(request_dict):
        try:
            flows.create_k8s_resource(annotation_data)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"backend error, reason: {str(e)}"
            )


@app.post("/mutate")
async def mutation(request_data: Request):
    content_validation(request_data)
    request_dict = await request_data.json()
    logger.info(f"`requst_json`: {request_dict}")
    admission_resource_create(request_dict)
    uid = admission_uid_parse(request_dict)
    content = {
        "apiVersion": "admission.k8s.io/v1",
        "kind": "AdmissionReview",
        "response": {
            "uid": uid,
            "allowed": True,
            "status": {"code": 200, "message": "ok"},
        },
    }
    return JSONResponse(content=content)
