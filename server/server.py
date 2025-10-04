import grpc
import generated.sample_pb2 as sample_pb2
import generated.sample_pb2_grpc as sample_pb2_grpc

def run():
    # 서버 연결
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = sample_pb2_grpc.CostServiceStub(channel)

        # 요청 메시지 생성
        query = sample_pb2.StatisticsQuery(
            filter=[sample_pb2.Filter(k="provider", v="azure", o="eq")]
        )

        # 서버에 요청 보내기
        response = stub.Stat(query)
        print("서버 응답:", response.results)

if __name__ == "__main__":
    run()
