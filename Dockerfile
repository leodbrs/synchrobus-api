FROM python:3.11.1

WORKDIR /usr/src/app
COPY ./src/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src/ .