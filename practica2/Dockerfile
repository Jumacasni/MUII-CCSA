FROM python:3.7-slim

ENV PORT 8000

WORKDIR api

COPY . /api/

RUN pip install --requirement requirements.txt

EXPOSE 8000

CMD gunicorn -w 4 -b 0.0.0.0:8000 api:app