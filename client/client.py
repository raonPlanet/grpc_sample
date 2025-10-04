import grpc
from google.protobuf import struct_pb2, json_format
import generated.sample_pb2 as sample_pb2
import generated.sample_pb2_grpc as sample_pb2_grpc

def run():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = sample_pb2_grpc.CostServiceStub(channel)
        query = sample_pb2.StatisticsQuery(
            filter=[sample_pb2.Filter(k="provider", v="azure", o="eq")]
        )
        print("Stat:", stub.Stat(query).results)

if __name__ == "__main__":
    run()