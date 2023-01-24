FROM python:3.11.1

WORKDIR /usr/src/app
COPY ./src/ .
RUN pip install --no-cache-dir -r requirements.txt
RUN chmod +x entrypoint.sh

ENTRYPOINT [ "./entrypoint.sh" ]