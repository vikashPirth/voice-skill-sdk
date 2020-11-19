FROM python:3.7-buster

COPY ./scripts/* /usr/local/bin/
COPY . /app
WORKDIR /app

RUN pip install --upgrade pip && \
    pip install skill_sdk*.whl

# The http port
EXPOSE 4242

CMD run
