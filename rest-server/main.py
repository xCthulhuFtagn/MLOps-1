from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict
from pydantic import BaseModel, Json
from pandas import DataFrame

from modules.services.auth_service import AuthService
from modules.services.model_trainer_service import ModelTrainService
from modules.services.data_version_tracker_service import DataVersionTrackerService

import pandas as pd
from starlette.background import BackgroundTask
from fastapi.responses import JSONResponse

auth_scheme = HTTPBearer()

authentificator = AuthService()
model_trainer = ModelTrainService()
data_version_tracker_service = DataVersionTrackerService(
    repo_path=".",
    endpoint_url='http://localhost:9000',
    access_key='your_access_key',
    secret_key='your_secret_key'
)
data_version_tracker_service.init_dvc()

app = FastAPI()


class HealthCheckResponse(BaseModel):
    status: str

class LoginResponse(BaseModel):
    token: str

class RegisterResponse(BaseModel):
    token: str

# class TrainModelRequest(BaseModel):
#     model_class: str
#     hyper_params: Dict  = {}

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
async def train_model(model_class: str = Form(),
                      hyper_params: Json = Form(),
                      features: UploadFile = File(),
                      labels: UploadFile = File(),
                      token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    if token is None:
        return {"error": "Invalid credentials"}

    is_token_valid = authentificator.checkToken(token.credentials)
    if is_token_valid is False:
        return {"error": "Invalid credentials"}

    if model_trainer.status_model.get(model_class, "not initialized") != "training":
        print("model is starting to train")

        # Define the bucket name dynamically
        bucket_name = f"s3://{model_class}"

        # Add datasets to DVC
        data_version_tracker_service.add_dataset(features.file, bucket_name, "features")
        data_version_tracker_service.add_dataset(labels.file, bucket_name, "labels")

        return JSONResponse(
            status_code=200,
            background=BackgroundTask(
                model_trainer.train,
                model_class,
                bucket_name,
                hyper_params,
                data_version_tracker_service
            ),
            content={"model_status": "training"}
        )
    else:
        return PermissionError("Model is already training")
            
@app.get("/check_model")
async def check_model(model_class: str,token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    if token is None:
        return {"error": "Invalid credentials"}
    
    is_token_valid = authentificator.checkToken(token.credentials)
    if is_token_valid is False:
        return {"error": "Invalid credentials"}
    
    response = model_trainer.status_model.get(model_class, f"No pretrained instance of {model_class}")
    print('response',response)
    return response

@app.get('/list_models')
async def list_models(token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    if token is None:
        return {"error": "Invalid credentials"}
    
    
    is_token_valid = authentificator.checkToken(token.credentials)
    if is_token_valid is False:
        return {"error": "Invalid credentials"}
    
    response =model_trainer.available_model_classes()
    return response

@app.post("/predict")
async def predict(model_class:str = Form(), 
                  file:UploadFile=File(),
                  token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    if token is None:
        return {"error": "Invalid credentials"}
    
    is_token_valid = authentificator.checkToken(token.credentials)
    if is_token_valid is False:
        return {"error": "Invalid credentials"}

    if not file.filename.endswith("csv"):
        raise TypeError("Wrong file format, only working with .csv")
    
    df = pd.read_csv(file.file, index_col=0) 

    response = DataFrame(model_trainer.predict(model_class, df)).astype(float)

    return response