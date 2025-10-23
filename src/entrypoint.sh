#!/bin/sh

python /usr/src/app/InitDb.py

# Use reload flag only in development
if [ "$ENVIRONMENT" = "development" ]; then
    uvicorn main:app --host 0.0.0.0 --port 8080 --reload
else
    uvicorn main:app --host 0.0.0.0 --port 8080
fi