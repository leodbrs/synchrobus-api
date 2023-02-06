#!/bin/sh

python /usr/src/app/InitDb.py
uvicorn main:app --host 0.0.0.0 --port 8080