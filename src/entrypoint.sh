#!/bin/sh

# ROOT_DIR=$(pwd)

# cd "$ROOT_DIR/database"
# rm -fr "$ROOT_DIR/database/alembic/versions/*"
# alembic revision --autogenerate
# alembic upgrade heads

# cd "$ROOT_DIR"
python /usr/src/app/InitDb.py
python /usr/src/app/main.py
