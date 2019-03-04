FROM python:3.7.2
ENV APP_HOME /app
RUN pip install pipenv
WORKDIR /app
