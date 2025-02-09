FROM python:3.9-slim

COPY . .

RUN pip install -r ./requirements.docker.txt --no-cache

CMD ["python", "./main.py"]
