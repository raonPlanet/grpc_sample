# README.md (gRPC VSCode Project Guide)

## 📘 개요
이 문서는 **VSCode에서 gRPC 프로젝트를 처음부터 끝까지** 실행할 수 있도록 정리한 가이드입니다.  
- 폴더 구조 생성 → 가상환경(venv) → requirements 설치  
- proto 작성 및 컴파일  
- 서버/클라이언트 실행  
- BloomRPC/Postman 테스트  
- Struct/Value를 활용한 동적 타입 실습  

## 📂 폴더 구조
```
grpc_sample/
 ├─ proto/              # proto 파일
 │    └─ sample.proto
 ├─ server/             # 서버 코드
 │    └─ server.py
 ├─ client/             # 클라이언트 코드
 │    └─ client.py
 ├─ generated/          # proto 컴파일 산출물
 ├─ venv/               # 가상환경
 └─ requirements.txt    # 패키지 목록
```

## 🔧 가상환경 생성 및 인터프리터 설정
```bash
python -m venv venv
venv\Scripts\Activate.ps1
```
- VSCode → `Python: Select Interpreter` → `./venv/Scripts/python.exe`

## 📦 requirements.txt
```text
grpcio==1.64.1
grpcio-tools==1.64.1
protobuf>=5.26.1
```
설치:
```bash
pip install -r requirements.txt
```

## 📑 proto 작성 (proto/sample.proto)
```proto
syntax = "proto3";

package sample;
import "google/protobuf/struct.proto";

service CostService {
  rpc Stat (StatisticsQuery) returns (StatisticsReply);
  rpc EchoValue (google.protobuf.Value) returns (google.protobuf.Value);
  rpc EchoStruct (google.protobuf.Struct) returns (google.protobuf.Struct);
  rpc SumCosts (google.protobuf.Struct) returns (SumReply);
  rpc FilterByProvider (google.protobuf.Struct) returns (google.protobuf.Struct);
  rpc EchoStructAsJson (google.protobuf.Struct) returns (google.protobuf.Struct);
}

message Filter {
  string k = 1;
  string v = 2;
  string o = 3;
}

message StatisticsQuery {
  repeated Filter filter = 1;
}

message StatisticsReply {
  map<string, double> results = 1;
}

message SumReply {
  double total = 1;
}
```

## 🛠 proto 컴파일
```bash
python -m grpc_tools.protoc -I./proto --python_out=./generated --grpc_python_out=./generated ./proto/sample.proto
```

## 🚀 서버 실행 (server/server.py)
```python
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
```

## 💻 클라이언트 실행 (client/client.py)
```python
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
```

## ▶ 실행 순서
```bash
# 1) 가상환경 활성화
venv\Scripts\Activate.ps1

# 2) 의존성 설치
pip install -r requirements.txt

# 3) proto 컴파일
python -m grpc_tools.protoc -I./proto --python_out=./generated --grpc_python_out=./generated ./proto/sample.proto

# 4) 서버 실행 (터미널 1)
python -m server.server

# 5) 클라이언트 실행 (터미널 2)
python -m client.client
```

## 🌐 BloomRPC 테스트 (공식 JSON 포맷)

### 1) EchoValue 요청
```json
{
  "listValue": {
    "values": [
      { "stringValue": "a" },
      { "numberValue": 1 },
      { "boolValue": true }
    ]
  }
}
```
응답: 동일한 Value 반환

### 2) EchoStruct 요청
```json
{
  "fields": {
    "msg": { "stringValue": "hi" },
    "enabled": { "boolValue": true }
  }
}
```
응답: 동일한 Struct 반환

### 3) SumCosts 요청
```json
{
  "fields": {
    "items": {
      "listValue": {
        "values": [
          { "structValue": { "fields": { "usd_cost": { "numberValue": 120.5 } } } },
          { "structValue": { "fields": { "usd_cost": { "numberValue": 80 } } } }
        ]
      }
    }
  }
}
```
응답:
```json
{ "total": 200.5 }
```

---

📌 이 README는 **최종 실행 안내서**로, 프로젝트를 처음부터 끝까지 따라 할 수 있으며, BloomRPC에서 Struct/Value 구조까지 테스트할 수 있도록 샘플 JSON과 예상 응답을 포함했습니다.
