import grpc
from concurrent import futures
from google.protobuf import struct_pb2, json_format
import json
import generated.sample_pb2 as sample_pb2
import generated.sample_pb2_grpc as sample_pb2_grpc

class CostService(sample_pb2_grpc.CostServiceServicer):
    def Stat(self, request, context):
        print("받은 요청:", request)
        results = {"azure": 200.0, "aws": 150.0}
        return sample_pb2.StatisticsReply(results=results)

    def EchoValue(self, request, context):
        return request

    def EchoStruct(self, request, context):
        return request

    def SumCosts(self, request, context):
        req = json_format.MessageToDict(request)
        items = req.get("items", [])
        total = sum(float(row.get("usd_cost", 0)) for row in items if isinstance(row, dict))
        return sample_pb2.SumReply(total=total)

    def FilterByProvider(self, request, context):
        req = json_format.MessageToDict(request)
        want = req.get("provider")
        data = req.get("data", [])
        filtered = [row for row in data if row.get("provider") == want]
        out = struct_pb2.Struct()
        json_format.ParseDict({"data": filtered}, out)
        return out

    def EchoStructAsJson(self, request, context):
        as_json = json_format.MessageToJson(request)
        out = struct_pb2.Struct()
        json_format.ParseDict({"as_json": as_json}, out)
        return out

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sample_pb2_grpc.add_CostServiceServicer_to_server(CostService(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("🚀 gRPC 서버 실행 중: localhost:50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()