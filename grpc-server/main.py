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

class ModelTrainerServicer(model_trainer_pb2_grpc.ModelTrainerServicer):
    def __init__(self):
        self.__authenticatorService = AuthService()
        self.__trainService = ModelTrainService()

    def Train(self, request, context):
        isAuth = self.__authenticatorService.checkToken(token=request.token)
        if isAuth == False: 
            error_response = model_trainer_pb2.TrainResponse(error= errors_pb2.Error(code=401,message="Unauthorized"))
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Unauthorized')
            return error_response
        try:
            self.__trainService.train(model_class=request.modelClass,hyper_params=request.hyperParams)
        except Exception as e:
            error_response = model_trainer_pb2.GetPredictionResponse(error= errors_pb2.Error(code=500,message=str(e)))
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return error_response
        return model_trainer_pb2.TrainResponse(modelClass=request.modelClass)
    
    def ListAvailableModels(self, request, context):
        isAuth = self.__authenticatorService.checkToken(token=request.token)
        if isAuth == False: 
            error_response = model_trainer_pb2.TrainResponse(error= errors_pb2.Error(code=401,message="Unauthorized"))
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Unauthorized')
            return error_response
        available_models = self.__trainService.available_model_classes()
        return model_trainer_pb2.ListAvailableModelsResponse(modelClasses=available_models)
    
    def GetPrediction(self, request:model_trainer_pb2.GetPredictionRequest, context):
        file = io.BytesIO(request.fileData)
        df = pd.read_csv(request.fileData, index_col=0) 
        # ReadCsvBuffer[bytes]
        
        isAuth = self.__authenticatorService.checkToken(token=request.token)
        if isAuth == False: 
            error_response = model_trainer_pb2.TrainResponse(error= errors_pb2.Error(code=401,message="Unauthorized"))
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Unauthorized')
            return error_response
        try:
            prediction = self.__trainService.predict(model_class=request.modelClass, inference_data=df)
        except Exception as e:
            error_response = model_trainer_pb2.GetPredictionResponse(error= errors_pb2.Error(code=500,message= str(e)))
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return error_response
        return model_trainer_pb2.GetPredictionResponse(prediction=prediction)
    
class HealthCheckServicer(healthcheck_pb2_grpc.HealthCheckServicer):
    def HealthCheck(self, request, context):
        return healthcheck_pb2.HealthcheckResponse(status="UP")
        
class AuthenticatorServicer(authenticator_pb2_grpc.AuthenticatorServicer):
    def __init__(self):
        self.__authenticatorService = AuthService()

    def Register(self, request, context):
        registerResult =  self.__authenticatorService.register(username=request.username, password=request.password)
        if registerResult is None:
            error_response = authenticator_pb2.RegisterResponse(error= errors_pb2.Error(code=500,message="Registration failed"))
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Registration failed')
            return error_response
        return authenticator_pb2.RegisterResponse(token=registerResult)
    def Login(self,request,context):
        loginResult = self.__authenticatorService.login(username=request.username, password=request.password)
        if loginResult is None:
            error_response = authenticator_pb2.LoginResponse(error = errors_pb2.Error(code=500,message="Login failed"))
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Login failed')
            return error_response
        return authenticator_pb2.LoginResponse(token=loginResult)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    authenticator_pb2_grpc.add_AuthenticatorServicer_to_server(AuthenticatorServicer(), server)
    healthcheck_pb2_grpc.add_HealthCheckServicer_to_server(HealthCheckServicer(), server)
    model_trainer_pb2_grpc.add_ModelTrainerServicer_to_server(ModelTrainerServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    print("Server is running on port 50051")
    serve()

    # python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. authenticator.proto