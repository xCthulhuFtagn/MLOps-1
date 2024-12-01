#!/bin/sh
cd ./rest-server && PYTHONPATH=.. uvicorn main:app --host 0.0.0.0 --reload
