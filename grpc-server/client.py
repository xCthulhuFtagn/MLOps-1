import grpc
import model_learner_pb2
import model_learner_pb2_grpc
import authenticator_pb2_grpc
import authenticator_pb2
import healthcheck_pb2
import healthcheck_pb2_grpc
import google.protobuf.empty_pb2; 

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = healthcheck_pb2_grpc.HealthCheckStub(channel)
        empty = google.protobuf.empty_pb2.Empty()
        response = stub.HealthCheck(request = empty)
    print(f"Result: {response}")

if __name__ == '__main__':
    run()