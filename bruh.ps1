pip install grpc_tools
python -m grpc_tools.protoc -I=protos/ --python_out=. --grpc_python_out=. .\protos\marketplace.proto