FROM python:3.12.0-slim

WORKDIR /src

COPY requirements.lock requirements-dev.lock ./

RUN sed '/-e/d' requirements.lock > requirements.txt && \
  pip install -r requirements.txt

COPY ./src/ .

EXPOSE 5000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
