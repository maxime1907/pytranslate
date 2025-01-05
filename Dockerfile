FROM python:3.12-alpine

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir --prefer-binary .

CMD ["pytranslate"]
