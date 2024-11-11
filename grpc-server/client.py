import grpc
import model_trainer_pb2
import model_trainer_pb2_grpc
import authenticator_pb2_grpc
import authenticator_pb2
import healthcheck_pb2
import healthcheck_pb2_grpc
import google.protobuf.empty_pb2; 

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub0 = authenticator_pb2_grpc.AuthenticatorStub(channel)
        stub1 = model_trainer_pb2_grpc.ModelTrainerStub(channel)
        stub2 = healthcheck_pb2_grpc.HealthCheckStub(channel)
        # read file
        with open("classifier_features.csv", "rb") as features:# opening for [r]eading as [b]inary
            featureData = features.read()
        with open("classifier_labels.csv", "rb") as labels:
            labelData = labels.read()
        # request = authenticator_pb2.RegisterRequest(
        #     username="max1777",
        #     password="max"
        # )
        # response = stub0.Register(request)
        # print(response)
        request = authenticator_pb2.LoginRequest(
            username="max1777",
            password="max"
        )
        response = stub0.Login(request)
        print(response.token)
        request = model_trainer_pb2.TrainRequest(
            modelClass='GradientBoostingClassifier',
            features=featureData, 
            labels=labelData,
            token=response.token
        )
        response = stub1.Train(request)
    print(f"Result: {response}")

if __name__ == '__main__':
    run()