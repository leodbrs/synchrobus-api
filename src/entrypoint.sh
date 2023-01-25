#!/bin/sh

ROOT_DIR=$(pwd)

cd "$ROOT_DIR/database"
alembic revision --autogenerate
alembic upgrade heads

cd "$ROOT_DIR"
python main.py
