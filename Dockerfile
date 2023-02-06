FROM python:3.11.1-alpine as base
FROM base as builder

RUN mkdir /install
WORKDIR /usr/src/app

RUN python -m venv /usr/src/app/venv
ENV PATH="/usr/src/app/venv/bin:$PATH"

COPY ./requirements.txt requirements.txt

RUN pip install -r requirements.txt

FROM base

WORKDIR /usr/src/app

COPY --from=builder /usr/src/app/venv ./venv
COPY ./src/ .

ENV PATH="/usr/src/app/venv/bin:$PATH"

COPY ./src/database database

WORKDIR /usr/src/app/database
RUN alembic init alembic
RUN sed -i 's/target_metadata = None/target_metadata = Base.metadata/g' alembic/env.py
RUN sed -i '/^from alembic import context/a from Table import Base' alembic/env.py
RUN alembic revision --autogenerate -m "init"
RUN alembic upgrade head

RUN chmod +x /usr/src/app/entrypoint.sh

WORKDIR /usr/src/app
ENTRYPOINT [ "/usr/src/app/entrypoint.sh" ]