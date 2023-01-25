FROM python:3.11.1-alpine as base
FROM base as builder

RUN mkdir /install
WORKDIR /usr/src/app

RUN python -m venv /usr/src/app/venv
ENV PATH="/usr/src/app/venv/bin:$PATH"

COPY ./src/requirements.txt requirements.txt

RUN pip install -r requirements.txt

FROM base

WORKDIR /usr/src/app

COPY --from=builder /usr/src/app/venv ./venv
COPY ./src/ .

ENV PATH="/usr/src/app/venv/bin:$PATH"
RUN chmod +x ./entrypoint.sh

ENTRYPOINT [ "./entrypoint.sh" ]