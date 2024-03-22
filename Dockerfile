FROM python:3.9

WORKDIR /app

COPY lambda/src/ .
COPY lambda/requirements.txt .

RUN pip install -r requirements.txt

CMD ["python", "lambda_function.py"]