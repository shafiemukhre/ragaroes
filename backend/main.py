from fastapi import FastAPI
# from fastapi.openapi.utils import get_openapi
import logging

from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
# from app.utils.openapi import patch_openapi
# from app.data.messages.status_code import StatusCode
# from app.data.messages.response import CustomHTTPException
# from app.routers.qa import qa_router
# from app.routers.admin import admin_router
from app.chatbot import chatbot_router
# from app.utils.log_util import logger
import uvicorn
import time

from app.rag_server import load_pdfs


# from asgiref.sync import async_to_sync
# from bugsnag.handlers import BugsnagHandler
# from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

# from pipeline import (
#     create_all_user_context,
#     make_all_response_decisions,
#     take_all_actions,
# )
# from pipeline.config import load_config


#TODO: Logging not working

app = FastAPI(
    title="Api Definitions for Question Answering",
    servers=[
        {
            "url": "http://127.0.0.1:8000",
            "description": "Local test environment",
        },
    ],
    version="0.0.1",
)

# Enable CORS for *
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger = logging.getLogger(__name__)

@app.middleware("timing")
async def add_response_timing_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    end_time = time.time()
    response.headers["X-Response-Time"] = str((end_time - start_time) * 1000)
    return response


# Remove 422 error in the api docs
# patch_openapi(app)
prefix = "/api/v1"
# app.include_router(qa_router, prefix=prefix)


#NOTE: SETUP
# load_pdfs()

app.include_router(chatbot_router, prefix=prefix)
# app.include_router(admin_router, prefix=prefix)


def handle_error_msg(request, error_msg, error_code=None):
    request_url = str(request.url)
    error_msg = f"client error in {request_url}: {error_msg}"
    logger.error(error_msg)
    result = error_msg.split(":")[-1].strip()
    return result


@app.exception_handler(HTTPException)
async def custom_exception_handler(request, exc):
    msg = exc.detail
    error_msg = handle_error_msg(request, msg)
    return JSONResponse(
        status_code=400,
        content={
            "status_code": exc.custom_status_code,
            "msg": error_msg,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    msg = exc.errors()[0]["msg"]
    error_msg = handle_error_msg(request, msg)
    return JSONResponse(
        status_code=400,
        content={
            "status_code":  404, #StatusCode.ERROR_INPUT_FORMAT,
            "msg": error_msg,
        },
    )


@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    error_msg = handle_error_msg(request, str(exc))
    return JSONResponse(
        status_code=400,
        content={
            "status_code": 404, #StatusCode.ERROR_INPUT_FORMAT,
            "msg": error_msg,
        },
    )


@app.exception_handler(KeyError)
async def key_error_handler(request, exc):
    error_msg = handle_error_msg(request, "KeyError - " + str(exc))
    return JSONResponse(
        status_code=400,
        content={
            "status_code": 404, #StatusCode.ERROR_INPUT_FORMAT,
            "msg": error_msg,
        },
    )


def main():
    # show if there is any python process running bounded to the port
    # ps -fA | grep python
    
    # load_pdfs()
    logger.info("Start api server")
    uvicorn.run("main:app", host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()