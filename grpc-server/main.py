import grpc
from concurrent import futures
import model_trainer_pb2
import model_trainer_pb2_grpc
import authenticator_pb2
import authenticator_pb2_grpc
import errors_pb2
import errors_pb2_grpc
import healthcheck_pb2
import healthcheck_pb2_grpc
import io
import os
import pandas as pd
import logging
from modules.services.auth_service import AuthService
from modules.services.model_trainer_service import ModelTrainService
from modules.utils.path_manager import makeRelPath
from modules.utils.logger import makeLogger

logger = makeLogger('grpc_server_logger', makeRelPath(os.getcwd(), "logs") + "grpc_server.log")

class ModelTrainerServicer(model_trainer_pb2_grpc.ModelTrainerServicer):
    """Service for training and managing machine learning models."""
    def __init__(self):
        self.__authenticatorService = AuthService()
        self.__trainService = ModelTrainService()
        logger.info("ModelTrainerServicer initialized")

    def Train(self, request, context):
        """Handles training of a model with specified class and hyperparameters.
        
        Args:
            request: TrainRequest containing token, model class, and hyperparameters.
            context: gRPC context for handling errors and status.
        
        Returns:
            TrainResponse with model class and potential error information.
        """
        logger.info(f"Training request received for model class: {request.modelClass}")
        isAuth = self.__authenticatorService.checkToken(token=request.token)
        if not isAuth:
            logger.warning("Unauthorized access attempt for training")
            error_response = model_trainer_pb2.TrainResponse(error=errors_pb2.Error(code=401, message="Unauthorized"))
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Unauthorized')
            return error_response
        try:
            logger.info(f"Starting training for model class: {request.modelClass} with hyperparameters: {request.hyperParams}")
            self.__trainService.train(model_class=request.modelClass, hyper_params=request.hyperParams)
            logger.info(f"Training completed successfully for model class: {request.modelClass}")
        except Exception as e:
            logger.error(f"Training error for model class {request.modelClass}: {str(e)}", exc_info=True)
            error_response = model_trainer_pb2.GetPredictionResponse(error=errors_pb2.Error(code=500, message=str(e)))
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return error_response
        return model_trainer_pb2.TrainResponse(modelClass=request.modelClass)

    def ListAvailableModels(self, request, context):
        """Returns a list of available model classes that can be trained.
        
        Args:
            request: ListAvailableModelsRequest containing token.
            context: gRPC context for handling errors and status.
        
        Returns:
            ListAvailableModelsResponse with a list of model classes and potential error information.
        """
        logger.info("List available models request received")
        isAuth = self.__authenticatorService.checkToken(token=request.token)
        if not isAuth:
            logger.warning("Unauthorized access attempt for listing models")
            error_response = model_trainer_pb2.TrainResponse(error=errors_pb2.Error(code=401, message="Unauthorized"))
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Unauthorized')
            return error_response
        available_models = self.__trainService.available_model_classes()
        logger.info(f"Available models retrieved: {available_models}")
        return model_trainer_pb2.ListAvailableModelsResponse(modelClasses=available_models)

    def GetPrediction(self, request: model_trainer_pb2.GetPredictionRequest, context):
        """Generates a prediction based on the provided model and data.
        
        Args:
            request: GetPredictionRequest containing token, model class, and file data.
            context: gRPC context for handling errors and status.
        
        Returns:
            GetPredictionResponse with prediction results and potential error information.
        """
        logger.info(f"Prediction request received for model class: {request.modelClass}")
        file = io.BytesIO(request.fileData)
        try:
            df = pd.read_csv(file, index_col=0)
            logger.info(f"Input data read successfully for model class: {request.modelClass}")
        except Exception as read_err:
            logger.error(f"Failed to read input data for prediction: {str(read_err)}", exc_info=True)
            error_response = model_trainer_pb2.GetPredictionResponse(error=errors_pb2.Error(code=400, message="Invalid input data format"))
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Invalid input data format')
            return error_response
        
        isAuth = self.__authenticatorService.checkToken(token=request.token)
        if not isAuth:
            logger.warning("Unauthorized access attempt for prediction")
            error_response = model_trainer_pb2.TrainResponse(error=errors_pb2.Error(code=401, message="Unauthorized"))
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Unauthorized')
            return error_response
        try:
            logger.info(f"Performing prediction for model class: {request.modelClass}")
            prediction = self.__trainService.predict(model_class=request.modelClass, inference_data=df)
            logger.info(f"Prediction completed successfully for model class: {request.modelClass}")
        except Exception as e:
            logger.error(f"Prediction error for model class {request.modelClass}: {str(e)}", exc_info=True)
            error_response = model_trainer_pb2.GetPredictionResponse(error=errors_pb2.Error(code=500, message=str(e)))
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return error_response
        return model_trainer_pb2.GetPredictionResponse(prediction=prediction)

class HealthCheckServicer(healthcheck_pb2_grpc.HealthCheckServicer):
    """Service for health checking the server status."""
    def HealthCheck(self, request, context):
        """Returns the status of the service.
        
        Args:
            request: HealthCheckRequest.
            context: gRPC context.
        
        Returns:
            HealthcheckResponse with the status of the service.
        """
        logger.info("Health check endpoint accessed")
        return healthcheck_pb2.HealthcheckResponse(status="UP")
        
class AuthenticatorServicer(authenticator_pb2_grpc.AuthenticatorServicer):
    """Service for handling user authentication."""
    def __init__(self):
        self.__authenticatorService = AuthService()
        logger.info("AuthenticatorServicer initialized")

    def Register(self, request, context):
        """Registers a new user and returns a token.
        
        Args:
            request: RegisterRequest containing username and password.
            context: gRPC context for handling errors and status.
        
        Returns:
            RegisterResponse with token or error information.
        """
        logger.info(f"Registration request received for user: {request.username}")
        registerResult = self.__authenticatorService.register(username=request.username, password=request.password)
        if registerResult is None:
            logger.error(f"Registration failed for user: {request.username}")
            error_response = authenticator_pb2.RegisterResponse(error=errors_pb2.Error(code=500, message="Registration failed"))
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Registration failed')
            return error_response
        logger.info(f"User registered successfully: {request.username}")
        return authenticator_pb2.RegisterResponse(token=registerResult)
    
    def Login(self, request, context):
        """Logs in a user and returns a token.
        
        Args:
            request: LoginRequest containing username and password.
            context: gRPC context for handling errors and status.
        
        Returns:
            LoginResponse with token or error information.
        """
        logger.info(f"Login request received for user: {request.username}")
        loginResult = self.__authenticatorService.login(username=request.username, password=request.password)
        if loginResult is None:
            logger.error(f"Login failed for user: {request.username}")
            error_response = authenticator_pb2.LoginResponse(error=errors_pb2.Error(code=500, message="Login failed"))
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Login failed')
            return error_response
        logger.info(f"User logged in successfully: {request.username}")
        return authenticator_pb2.LoginResponse(token=loginResult)

def serve():
    """Starts the gRPC server and listens for incoming requests."""
    logger.info("Starting gRPC server on port 50051")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    authenticator_pb2_grpc.add_AuthenticatorServicer_to_server(AuthenticatorServicer(), server)
    healthcheck_pb2_grpc.add_HealthCheckServicer_to_server(HealthCheckServicer(), server)
    model_trainer_pb2_grpc.add_ModelTrainerServicer_to_server(ModelTrainerServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logger.info("Server is running on port 50051")
    serve()
