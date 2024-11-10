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
import pandas as pd

from modules.services.auth_service import AuthService
from modules.services.model_trainer_service import ModelTrainService

# Настройка логгирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ModelTrainerServicer(model_trainer_pb2_grpc.ModelTrainerServicer):
    def __init__(self):
        self.__authenticatorService = AuthService()
        self.__trainService = ModelTrainService()

    def Train(self, request, context):
        logger.info("Received training request for model class: %s", request.modelClass)
        isAuth = self.__authenticatorService.checkToken(token=request.token)
        if not isAuth:
            logger.warning("Unauthorized access attempt for model training")
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Unauthorized')
            return model_trainer_pb2.TrainResponse(error=errors_pb2.Error(code=401, message="Unauthorized"))
        
        try:
            logger.info("Starting training for model class: %s", request.modelClass)
            self.__trainService.train(model_class=request.modelClass, hyper_params=request.hyperParams)
            logger.info("Model %s trained successfully", request.modelClass)
        except Exception as e:
            logger.error("Error occurred during model training: %s", str(e), exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return model_trainer_pb2.TrainResponse(error=errors_pb2.Error(code=500, message=str(e)))
        
        return model_trainer_pb2.TrainResponse(modelClass=request.modelClass)

    def ListAvailableModels(self, request, context):
        logger.info("ListAvailableModels request received")
        isAuth = self.__authenticatorService.checkToken(token=request.token)
        if not isAuth:
            logger.warning("Unauthorized access attempt for listing models")
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Unauthorized')
            return model_trainer_pb2.ListAvailableModelsResponse(error=errors_pb2.Error(code=401, message="Unauthorized"))
        
        available_models = self.__trainService.available_model_classes()
        logger.info("Available models listed: %s", available_models)
        return model_trainer_pb2.ListAvailableModelsResponse(modelClasses=available_models)

    def GetPrediction(self, request, context):
        logger.info("GetPrediction request received for model class: %s", request.modelClass)
        isAuth = self.__authenticatorService.checkToken(token=request.token)
        if not isAuth:
            logger.warning("Unauthorized access attempt for prediction")
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Unauthorized')
            return model_trainer_pb2.GetPredictionResponse(error=errors_pb2.Error(code=401, message="Unauthorized"))
        
        try:
            file = io.BytesIO(request.fileData)
            df = pd.read_csv(file, index_col=0)
            logger.info("Dataframe loaded successfully for prediction")
            prediction = self.__trainService.predict(model_class=request.modelClass, inference_data=df)
            logger.info("Prediction successful for model class: %s", request.modelClass)
        except Exception as e:
            logger.error("Error occurred during prediction: %s", str(e), exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return model_trainer_pb2.GetPredictionResponse(error=errors_pb2.Error(code=500, message=str(e)))
        
        return model_trainer_pb2.GetPredictionResponse(prediction=prediction)

class AuthenticatorServicer(authenticator_pb2_grpc.AuthenticatorServicer):
    def __init__(self):
        self.__authenticatorService = AuthService()

    def Register(self, request, context):
        logger.info("Registration request received for user: %s", request.username)
        registerResult = self.__authenticatorService.register(username=request.username, password=request.password)
        if registerResult is None:
            logger.error("Registration failed for user: %s", request.username)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Registration failed')
            return authenticator_pb2.RegisterResponse(error=errors_pb2.Error(code=500, message="Registration failed"))
        logger.info("User %s registered successfully", request.username)
        return authenticator_pb2.RegisterResponse(token=registerResult)

    def Login(self, request, context):
        logger.info("Login request received for user: %s", request.username)
        loginResult = self.__authenticatorService.login(username=request.username, password=request.password)
        if loginResult is None:
            logger.warning("Login failed for user: %s", request.username)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Login failed')
            return authenticator_pb2.LoginResponse(error=errors_pb2.Error(code=500, message="Login failed"))
        logger.info("User %s logged in successfully", request.username)
        return authenticator_pb2.LoginResponse(token=loginResult)

# Server setup
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    model_trainer_pb2_grpc.add_ModelTrainerServicer_to_server(ModelTrainerServicer(), server)
    authenticator_pb2_grpc.add_AuthenticatorServicer_to_server(AuthenticatorServicer(), server)
    server.add_insecure_port('[::]:50051')
    logger.info("Starting gRPC server on port 50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    print("Server is running on port 50051")
    serve()

    # python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. authenticator.proto
