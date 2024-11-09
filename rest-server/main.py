from fastapi import FastAPI, File, UploadFile, HTTPException, Header, Depends, Form
from fastapi.security  import HTTPBearer,HTTPAuthorizationCredentials
from typing import Dict
from pydantic import BaseModel
from pandas import DataFrame, Series


from modules.services.auth_service import AuthService
from modules.services.model_trainer_service import ModelTrainService

import pandas as pd

from starlette.background import BackgroundTask
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from typing import Annotated

auth_scheme = HTTPBearer()

# TODO:
# Add tokens to REST
# Handle exceptions in train
# Clean up grpc
# Write README
# Clean shell scripts
# Add pythonDocs for functions
# Get analytics:
#  Интерактивный дашборд streamlit/gradio/etc. (можно отдельным сервисом, просто его запуск должен быть прописан в инструкции)
authentificator = AuthService()
model_trainer = ModelTrainService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    # authentificator = AuthService()
    # model_trainer = ModelTrainService()
    yield

app = FastAPI(lifespan=lifespan)


class HealthCheckResponse(BaseModel):
    status: str

class LoginResponse(BaseModel):
    token: str

class RegisterResponse(BaseModel):
    token: str

class TrainModelRequest(BaseModel):
    model_class: str
    hyper_params: Dict  = {}


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
async def train_model(body: TrainModelRequest,token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    if token is None:
        return {"error": "Invalid credentials"}
    
    is_token_valid = authentificator.checkToken(token.credentials)
    if is_token_valid is False:
        return {"error": "Invalid credentials"}
    if model_trainer.status_model.get(body.model_class, "not initialized")  != "training":
        print("model is starting to train" )
        return JSONResponse(status_code=200, background=BackgroundTask(model_trainer.train, body.model_class, body.hyper_params), content={"model_status": "training"})
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
async def predict( model_class:str = Form(),file:UploadFile=File(),token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
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