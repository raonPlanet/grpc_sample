import grpc
from concurrent import futures
import generated.sample_pb2 as sample_pb2
import generated.sample_pb2_grpc as sample_pb2_grpc

class CostService(sample_pb2_grpc.CostServiceServicer):
    def Stat(self, request, context):
        print("받은 요청:", request)
        results = {"azure": 200.0, "aws": 150.0}
        return sample_pb2.StatisticsReply(results=results)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sample_pb2_grpc.add_CostServiceServicer_to_server(CostService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("🚀 gRPC 서버 실행 중: localhost:50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
