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
        stub = model_trainer_pb2_grpc.ModelTrainerStub(channel)
        stub2 = healthcheck_pb2_grpc.HealthCheckStub(channel)
        # read file
        in_file = open("classifier.csv", "rb") # opening for [r]eading as [b]inary
        fileData = in_file.read()
        in_file.close()
        request = model_trainer_pb2.GetPredictionRequest(modelClass='GradientBoostingClassifier',fileData=fileData,token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlc3QiLCJwYXNzd29yZCI6InRlc3QifQ.qnVlS_xg5AbXAjlmt8KLAdzoBR8XTIA3zPdHDelM5SI')
        response = stub.GetPrediction(request)
    print(f"Result: {response}")

if __name__ == '__main__':
    run()