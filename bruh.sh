pip install --upgrade pip

#python -m venv venv
#source venv/bin/activate

pip install grpcio grpcio-tools
python -m grpc_tools.protoc -I=protos/ --python_out=. --grpc_python_out=. ./protos/marketplace.proto