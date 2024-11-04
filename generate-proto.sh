#!/bin/sh

cd grpc &&
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. --pyi_out=. ./**.proto