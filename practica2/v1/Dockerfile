FROM python:3.7-slim

ENV PORT 8000

WORKDIR api_v1

COPY . /api_v1/

RUN pip install --upgrade pip && pip install --requirement requirements.txt

EXPOSE 8000

CMD python api_v1.py