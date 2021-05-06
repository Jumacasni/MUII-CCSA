FROM python:3.7-slim

ENV PORT 8000

WORKDIR /api/

COPY . /api/

RUN apt-get -y update  && apt-get install -y \
  python3-dev \
  apt-utils \
  python-dev \
  build-essential \
	&& rm -rf /var/lib/apt/lists/* \
	&& pip install --upgrade pip \
	&& pip install --upgrade setuptools \
	&& pip install --upgrade pandas \
	&& pip install --upgrade plotly \
	&& pip install --requirement requirements.txt

EXPOSE 8000

CMD gunicorn -w 4 -b 0.0.0.0:8000 api:app