from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import Dict
from pydantic import BaseModel

from modules.services.auth_service import AuthService
from modules.services.model_trainer_service import ModelTrainService

import pandas as pd

from starlette.background import BackgroundTask
from fastapi.responses import JSONResponse

# TODO:
# Add tokens to REST
# Handle exceptions in train
# Clean up grpc
# Write README
# Clean shell scripts
# Add pythonDocs for functions
# Get analytics:
#  Интерактивный дашборд streamlit/gradio/etc. (можно отдельным сервисом, просто его запуск должен быть прописан в инструкции)

app = FastAPI()

authentificator = AuthService()
model_trainer = ModelTrainService()

class HealthCheckResponse(BaseModel):
    status: str

class LoginResponse(BaseModel):
    token: str

class RegisterResponse(BaseModel):
    token: str


@app.get("/healthcheck",status_code=200)
async def healthcheck():
    return HealthCheckResponse(status="UP")

@app.post("/register")
async def register(username:str, password: str):
    response = authentificator.register(username, password)
    if response is None: 
        raise HTTPException(status_code=400, detail="Registration failed") 
    return RegisterResponse(token=response)

@app.post("/login")
async def login(username:str, password: str):
    response = authentificator.login(username, password)
    if response is None: 
        raise HTTPException(status_code=400, detail="Login failed") 
    return LoginResponse(token = response)

@app.post("/train_model")
async def train_model(username:str, password: str, model_class: str, hyper_params: Dict,token: Union[str, None] = Header(alias="Authorization",default=None)):
    token = authentificator.login(username, password)
    if token is None:
        return {"error": "Invalid credentials"}
    # response = model_trainer.train(model_class, hyper_params)
    if ModelTrainService.model_status[model_class] != "training":
        return JSONResponse(status_code=200, background=BackgroundTask(model_trainer.train, (model_class, hyper_params)), content={"model_status": "training"})
    else:
        return PermissionError("Model is already training")
    
@app.get("/check_model")
async def check_model(username:str, password: str, model_class: str):
    token = authentificator.login(username, password)
    if token is None:
        return {"error": "Invalid credentials"}
    response = ModelTrainService.model_status[model_class]
    return response
    
@app.post("/predict")
async def predict(username:str, password: str, model_class: str, data_file: UploadFile):
    token = authentificator.login(username, password)
    if token is None:
        return {"error": "Invalid credentials"}

    if not data_file.name.endswith("csv"):
        raise ValueError("Wrong file format, only working with .csv")
    
    df = pd.read_csv(data_file)
    if ModelTrainService.model_status[model_class] != "ready":
        if ModelTrainService.model_status[model_class] == "training":
            raise PermissionError("Model is still training")
        else:
            raise ModelTrainService.model_status[model_class]
    
    response = model_trainer.predict(model_class, df)

# @app.post("/predict")
# async def predict(username:str, password: str, model_class: str, data_file: UploadFile):
#     token = authentificator.login(username, password)
#     if token is None:
#         return {"error": "Invalid credentials"}

#     if not data_file.name.endswith("csv"):
#         raise ValueError("Wrong file format, only working with .csv")
    
#     df = pd.read_csv(data_file.file)
#     if ModelTrainService.model_status[model_class]:
#         raise PermissionError("Model still in training")
    
#     response = model_trainer.predict(model_class, df)

    