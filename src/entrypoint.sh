#!/bin/bash

cd ./database
alembic revision --autogenerate
alembic upgrade heads

cd ../
python main.py
