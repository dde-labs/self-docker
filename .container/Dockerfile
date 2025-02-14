FROM python:3.9-alpine

COPY . .

RUN pip install -r ./requirements.docker.txt --no-cache \
    && rm -rf /root/.cache/pip

CMD ["python", "./main.py"]
