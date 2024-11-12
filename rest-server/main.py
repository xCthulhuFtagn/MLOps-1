import os
import logging
from fastapi import FastAPI, File, UploadFile, HTTPException, Header, Depends, Form
from fastapi.security  import HTTPBearer,HTTPAuthorizationCredentials
from typing import Dict
from pydantic import BaseModel
from pandas import DataFrame, Series
from modules.services.auth_service import AuthService
from modules.services.model_trainer_service import ModelTrainService
from modules.utils.path_manager import makeRelPath
from modules.utils.logger import makeLogger
import pandas as pd
from starlette.background import BackgroundTask
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import Annotated

logger = makeLogger('rest_server_logger', makeRelPath(os.getcwd(), "logs") + "rest_server.log")

auth_scheme = HTTPBearer()
authentificator = AuthService()
model_trainer = ModelTrainService()

app = FastAPI()

class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint.
    
    Attributes:
        status (str): Status of the service, typically "UP" if the service is running.
    """
    status: str

class LoginResponse(BaseModel):
    """Response model for the login endpoint.
    
    Attributes:
        token (str): Token returned upon successful authentication.
    """
    token: str

class RegisterResponse(BaseModel):
    """Response model for the register endpoint.
    
    Attributes:
        token (str): Token returned upon successful registration.
    """
    token: str

class TrainModelRequest(BaseModel):
    """Request model for training a model.
    
    Attributes:
        model_class (str): The class of the model to be trained.
        hyper_params (Dict): A dictionary of hyperparameters for the training process.
    """
    model_class: str
    hyper_params: Dict = {}

@app.get("/healthcheck", status_code=200)
async def healthcheck():
    """Check the health status of the service.
    
    Returns:
        HealthCheckResponse: An object containing the status of the service.
    """
    logger.info("Healthcheck endpoint accessed")
    return HealthCheckResponse(status="UP")

@app.post("/register")
async def register(username: str, password: str):
    """Register a new user.
    
    Args:
        username (str): The username for the new user.
        password (str): The password for the new user.

    Returns:
        dict: A dictionary containing the token if registration is successful.

    Raises:
        HTTPException: If the registration fails.
    """
    logger.info("Registration request received for user: %s", username)
    response = authentificator.register(username, password)
    if response is None:
        logger.error("Registration failed for user: %s", username)
        raise HTTPException(status_code=400, detail="Registration failed")
    logger.info("User registered successfully: %s", username)
    return {"token": response}

@app.post("/login")
async def login(username: str, password: str):
    """Authenticate a user and return a token.
    
    Args:
        username (str): The username of the user.
        password (str): The password of the user.

    Returns:
        dict: A dictionary containing the token if login is successful.

    Raises:
        HTTPException: If the login fails.
    """
    logger.info("Login request received for user: %s", username)
    response = authentificator.login(username, password)
    if response is None:
        logger.error("Login failed for user: %s", username)
        raise HTTPException(status_code=400, detail="Login failed")
    logger.info("User logged in successfully: %s", username)
    return {"token": response}

@app.post("/train_model")
async def train_model(body: TrainModelRequest, token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    """Initiate training for a specified model class with given hyperparameters.
    
    Args:
        body (TrainModelRequest): The request body containing model class and hyperparameters.
        token (HTTPAuthorizationCredentials): The token for user authentication.

    Returns:
        JSONResponse: A response indicating the training status.

    Raises:
        PermissionError: If the model is already in training.
        HTTPException: If authentication fails.
    """
    logger.info("Training model request received for model class: %s", body.model_class)
    if token is None:
        logger.error("Invalid credentials: No token provided")
        return {"error": "Invalid credentials"}

    is_token_valid = authentificator.checkToken(token.credentials)
    if not is_token_valid:
        logger.error("Invalid credentials for token: %s", token.credentials)
        return {"error": "Invalid credentials"}

    if model_trainer.status_model.get(body.model_class, "not initialized") != "training":
        logger.info("Model %s is starting to train", body.model_class)
        return JSONResponse(
            status_code=200,
            background=BackgroundTask(model_trainer.train, body.model_class, body.hyper_params),
            content={"model_status": "training"}
        )
    else:
        logger.warning("Model %s is already in training", body.model_class)
        return PermissionError("Model is already training")

@app.get("/check_model")
async def check_model(model_class: str, token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    """Check the training status of a specified model class.
    
    Args:
        model_class (str): The class of the model to check.
        token (HTTPAuthorizationCredentials): The token for user authentication.

    Returns:
        str or dict: The status of the model or an error message if authentication fails.
    """
    logger.info("Check model status request received for model class: %s", model_class)
    if token is None:
        logger.error("Invalid credentials: No token provided")
        return {"error": "Invalid credentials"}

    is_token_valid = authentificator.checkToken(token.credentials)
    if not is_token_valid:
        logger.error("Invalid credentials for token: %s", token.credentials)
        return {"error": "Invalid credentials"}

    response = model_trainer.status_model.get(model_class, f"No pretrained instance of {model_class}")
    logger.info("Model status for %s: %s", model_class, response)
    return response

@app.get('/list_models')
async def list_models(token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    """List all available model classes for training and prediction.
    
    Args:
        token (HTTPAuthorizationCredentials): The token for user authentication.

    Returns:
        list: A list of available model classes.
    """
    logger.info("List models request received")
    if token is None:
        logger.error("Invalid credentials: No token provided")
        return {"error": "Invalid credentials"}

    is_token_valid = authentificator.checkToken(token.credentials)
    if not is_token_valid:
        logger.error("Invalid credentials for token: %s", token.credentials)
        return {"error": "Invalid credentials"}

    response = model_trainer.available_model_classes()
    logger.info("Available models: %s", response)
    return response

@app.post("/predict")
async def predict(model_class: str = Form(), file: UploadFile = File(), token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    """Make a prediction using the specified model class and input CSV file.
    
    Args:
        model_class (str): The class of the model to use for prediction.
        file (UploadFile): The CSV file containing input data.
        token (HTTPAuthorizationCredentials): The token for user authentication.

    Returns:
        DataFrame: A DataFrame containing the prediction results.

    Raises:
        TypeError: If the file format is not CSV.
        HTTPException: If prediction fails due to an error.
    """
    logger.info("Prediction request received for model class: %s", model_class)
    if token is None:
        logger.error("Invalid credentials: No token provided")
        return {"error": "Invalid credentials"}

    is_token_valid = authentificator.checkToken(token.credentials)
    if not is_token_valid:
        logger.error("Invalid credentials for token: %s", token.credentials)
        return {"error": "Invalid credentials"}

    if not file.filename.endswith("csv"):
        logger.error("Invalid file format for file: %s", file.filename)
        raise TypeError("Wrong file format, only working with .csv")

    try:
        print(file.file)
        print(file)
        df = pd.read_csv(file.file, index_col=0)
        logger.info("CSV file read successfully for prediction")
        response = pd.DataFrame(model_trainer.predict(model_class, df)).astype(float)
        logger.info("Prediction completed for model class: %s", model_class)
    except Exception as e:
        logger.error("Error during prediction for model class %s: %s", model_class, str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Prediction failed")

    return response
