#!/bin/sh
cd ./rest-server && PYTHONPATH=.. uvicorn main:app --reload
